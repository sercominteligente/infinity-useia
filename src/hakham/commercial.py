from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .tool_gateway import ToolGateway


QUOTE_INTENT_RE = re.compile(r"\b(or[cç]amento|orcamento|proposta)\b", re.I)
APPROVAL_RE = re.compile(
    r"^(?:pode\s+enviar|pode\s+mandar|envia|mande|manda|pode\s+seguir|aprovado|aprovo)(?:[.!\s]*)$",
    re.I,
)
PHONE_RE = re.compile(r"(?:whats(?:app)?|telefone|fone|contato)\s*(?:[:=\-]|é|e)?\s*(\+?\d[\d\s().-]{7,})", re.I)
DIMENSION_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?\b", re.I)
CLIENT_PATTERNS = (
    re.compile(r"\bcliente\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ '\-.]{1,80}?)(?=\s+(?:de|com)\s+\d+\b|\s*,|\s+whats|\s+telefone|\s+fone|$)", re.I),
    re.compile(r"\bpara\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ '\-.]{1,80}?)(?=\s+(?:de|com)\s+\d+\b|\s*,|\s+whats|\s+telefone|\s+fone|$)", re.I),
)


def _money(value: Decimal) -> str:
    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    raw = f"{value:,.2f}"
    return "R$ " + raw.replace(",", "X").replace(".", ",").replace("X", ".")


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" ,.;:-")).strip()


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _to_meters(value: str, unit: str | None) -> Decimal:
    number = Decimal(value.replace(",", "."))
    normalized = (unit or "cm").casefold()
    if normalized == "m":
        return number
    if normalized == "mm":
        return number / Decimal("1000")
    return number / Decimal("100")


@dataclass(frozen=True)
class ParsedQuoteRequest:
    client_name: str
    whatsapp: str
    product_key: str
    quantity: int
    width_m: Decimal
    height_m: Decimal
    source_text: str


@dataclass(frozen=True)
class QuoteDraft:
    id: int
    document_number: str
    client_name: str
    whatsapp: str
    product_key: str
    product_name: str
    quantity: int
    width_m: Decimal
    height_m: Decimal
    area_unit_m2: Decimal
    area_total_m2: Decimal
    price_per_m2: Decimal
    unit_price: Decimal
    subtotal: Decimal
    discount: Decimal
    delivery_installation: Decimal
    total: Decimal
    payment_method: str
    validity: str
    status: str
    approval_fingerprint: str
    created_at: str
    pdf_path: str | None = None
    message_id: str | None = None


class CommercialCatalog:
    def __init__(self, path: str | None = None) -> None:
        load_dotenv()
        configured = (path or os.getenv("HAKHAM_COMMERCIAL_CATALOG", "")).strip()
        if configured:
            self.path = Path(configured)
        else:
            editable = Path("data/commercial_catalog.json")
            bundled = Path(__file__).resolve().parent / "data" / "commercial_catalog.json"
            self.path = editable if editable.is_file() else bundled
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.is_file():
            raise ValueError(f"catálogo comercial não encontrado: {self.path}")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("products"), dict):
            raise ValueError("catálogo comercial inválido")
        return payload

    def identify_product(self, text: str) -> tuple[str, dict[str, Any]] | None:
        lowered = text.casefold()
        candidates: list[tuple[int, str, dict[str, Any]]] = []
        for key, item in self.data["products"].items():
            for alias in item.get("aliases") or []:
                alias_text = str(alias).casefold().strip()
                if alias_text and re.search(rf"\b{re.escape(alias_text)}\b", lowered):
                    candidates.append((len(alias_text), str(key), item))
        if not candidates:
            return None
        _, key, item = max(candidates, key=lambda row: row[0])
        return key, item

    @property
    def rules(self) -> dict[str, Any]:
        value = self.data.get("rules")
        return value if isinstance(value, dict) else {}


class QuoteStore:
    def __init__(self, db_path: str = "data/hakham.db") -> None:
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS commercial_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_number TEXT UNIQUE,
                    session_id TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    whatsapp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    approval_fingerprint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    pdf_path TEXT,
                    message_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_quotes_session_status ON commercial_quotes(session_id, status, id DESC)")

    @staticmethod
    def _row_to_draft(row: sqlite3.Row) -> QuoteDraft:
        payload = json.loads(row["payload_json"])
        return QuoteDraft(
            id=int(row["id"]),
            document_number=str(row["document_number"]),
            client_name=str(row["client_name"]),
            whatsapp=str(row["whatsapp"]),
            product_key=str(payload["product_key"]),
            product_name=str(payload["product_name"]),
            quantity=int(payload["quantity"]),
            width_m=Decimal(payload["width_m"]),
            height_m=Decimal(payload["height_m"]),
            area_unit_m2=Decimal(payload["area_unit_m2"]),
            area_total_m2=Decimal(payload["area_total_m2"]),
            price_per_m2=Decimal(payload["price_per_m2"]),
            unit_price=Decimal(payload["unit_price"]),
            subtotal=Decimal(payload["subtotal"]),
            discount=Decimal(payload["discount"]),
            delivery_installation=Decimal(payload["delivery_installation"]),
            total=Decimal(payload["total"]),
            payment_method=str(payload["payment_method"]),
            validity=str(payload["validity"]),
            status=str(row["status"]),
            approval_fingerprint=str(row["approval_fingerprint"]),
            created_at=str(row["created_at"]),
            pdf_path=str(row["pdf_path"]) if row["pdf_path"] else None,
            message_id=str(row["message_id"]) if row["message_id"] else None,
        )

    def create(self, session_id: str, parsed: ParsedQuoteRequest, product: dict[str, Any], rules: dict[str, Any]) -> QuoteDraft:
        area_unit = (parsed.width_m * parsed.height_m).quantize(Decimal("0.0001"))
        area_total = (area_unit * parsed.quantity).quantize(Decimal("0.0001"))
        price_m2 = _decimal(product["price_per_m2"])
        unit_price = (area_unit * price_m2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal = (area_total * price_m2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        discount = Decimal("0.00")
        delivery = Decimal("0.00")
        total = subtotal - discount + delivery
        payload = {
            "product_key": parsed.product_key,
            "product_name": str(product["name"]),
            "quantity": parsed.quantity,
            "width_m": str(parsed.width_m),
            "height_m": str(parsed.height_m),
            "area_unit_m2": str(area_unit),
            "area_total_m2": str(area_total),
            "price_per_m2": str(price_m2),
            "unit_price": str(unit_price),
            "subtotal": str(subtotal),
            "discount": str(discount),
            "delivery_installation": str(delivery),
            "total": str(total),
            "payment_method": str(rules.get("payment_method") or "Não informado"),
            "validity": str(rules.get("validity") or "Não informado"),
        }
        snapshot = json.dumps(
            {"client": parsed.client_name, "whatsapp": parsed.whatsapp, **payload},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute(
                "UPDATE commercial_quotes SET status='superseded', updated_at=? WHERE session_id=? AND status='awaiting_approval'",
                (now, session_id),
            )
            cursor = db.execute(
                """
                INSERT INTO commercial_quotes(
                    document_number, session_id, client_name, whatsapp, payload_json,
                    approval_fingerprint, status, created_at, updated_at
                ) VALUES (NULL, ?, ?, ?, ?, ?, 'awaiting_approval', ?, ?)
                """,
                (session_id, parsed.client_name, parsed.whatsapp, json.dumps(payload, ensure_ascii=False), fingerprint, now, now),
            )
            quote_id = int(cursor.lastrowid)
            document_number = f"ORC-{datetime.now().year}-{quote_id:04d}"
            db.execute("UPDATE commercial_quotes SET document_number=? WHERE id=?", (document_number, quote_id))
            row = db.execute("SELECT * FROM commercial_quotes WHERE id=?", (quote_id,)).fetchone()
        return self._row_to_draft(row)

    def latest_pending(self, session_id: str) -> QuoteDraft | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM commercial_quotes WHERE session_id=? AND status='awaiting_approval' ORDER BY id DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        quote = self._row_to_draft(row)
        try:
            created = datetime.fromisoformat(quote.created_at)
            if datetime.now(timezone.utc) - created > timedelta(hours=24):
                return None
        except ValueError:
            return None
        return quote

    def mark_sent(self, quote_id: int, *, pdf_path: str, message_id: str | None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute(
                "UPDATE commercial_quotes SET status='sent', pdf_path=?, message_id=?, updated_at=? WHERE id=?",
                (pdf_path, message_id, now, quote_id),
            )


class QuoteParser:
    def __init__(self, catalog: CommercialCatalog) -> None:
        self.catalog = catalog

    def parse(self, message: str) -> tuple[ParsedQuoteRequest | None, list[str]]:
        missing: list[str] = []
        client = ""
        for pattern in CLIENT_PATTERNS:
            match = pattern.search(message)
            if match:
                client = _clean_name(match.group(1))
                break
        if not client:
            missing.append("nome do cliente")

        phone_match = PHONE_RE.search(message)
        phone = _digits(phone_match.group(1)) if phone_match else ""
        if len(phone) < 10:
            missing.append("WhatsApp com DDI e DDD")

        product_match = self.catalog.identify_product(message)
        if product_match is None:
            missing.append("produto reconhecido no catálogo")
            product_key = ""
        else:
            product_key = product_match[0]

        dim_match = DIMENSION_RE.search(message)
        width_m = height_m = Decimal("0")
        if dim_match:
            width_m = _to_meters(dim_match.group(1), dim_match.group(3))
            height_m = _to_meters(dim_match.group(2), dim_match.group(3))
        else:
            missing.append("medidas, por exemplo 120x80cm")

        quantity = 0
        if product_match is not None:
            aliases = [str(a) for a in product_match[1].get("aliases", [])]
            for alias in sorted(aliases, key=len, reverse=True):
                match = re.search(rf"\b(\d+)\s*(?:x\s*)?{re.escape(alias)}\b", message, flags=re.I)
                if match:
                    quantity = int(match.group(1))
                    break
        if quantity <= 0:
            generic = re.search(r"\b(?:de|com)?\s*(\d+)\s+[A-Za-zÀ-ÿ]", message, re.I)
            quantity = int(generic.group(1)) if generic else 0
        if quantity <= 0:
            missing.append("quantidade")

        if missing:
            return None, missing
        return ParsedQuoteRequest(client, phone, product_key, quantity, width_m, height_m, message), []


class QuotePDF:
    def __init__(self, output_dir: str = "data/commercial/quotes") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _draw_text_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body: str, stroke: colors.Color) -> None:
        c.setStrokeColor(stroke)
        c.setLineWidth(1)
        c.rect(x, y, w, h, stroke=1, fill=0)
        c.setFillColor(stroke)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(x + 8, y + h - 13, title.upper())
        c.setFillColor(colors.HexColor("#13223A"))
        c.setFont("Helvetica", 8.2)
        text = c.beginText(x + 8, y + h - 28)
        text.setLeading(11)
        for line in body.split("\n"):
            text.textLine(line[:92])
        c.drawText(text)

    @staticmethod
    def _try_logo(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> bool:
        candidates = [
            Path("assets/sercomtec-logo.base64"),
            Path(__file__).resolve().parents[2] / "assets" / "sercomtec-logo.base64",
        ]
        asset = next((item for item in candidates if item.is_file()), None)
        if asset is None:
            return False
        try:
            raw = base64.b64decode(asset.read_text(encoding="ascii").strip())
            c.drawImage(ImageReader(BytesIO(raw)), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto", anchor="sw")
            return True
        except Exception:
            return False

    def generate(self, quote: QuoteDraft) -> Path:
        safe_client = re.sub(r"[^A-Za-z0-9_-]+", "_", quote.client_name)
        path = self.output_dir / f"Orcamento_SER_{quote.document_number}_{safe_client}.pdf"
        c = canvas.Canvas(str(path), pagesize=A4)
        page_w, page_h = A4
        navy = colors.HexColor("#081D3A")
        blue = colors.HexColor("#168CF5")
        magenta = colors.HexColor("#FF1493")
        orange = colors.HexColor("#FF6A00")
        gray = colors.HexColor("#6D7889")
        light = colors.HexColor("#F6F8FB")

        c.setFillColor(blue); c.rect(0, page_h - 4, page_w / 3, 4, stroke=0, fill=1)
        c.setFillColor(magenta); c.rect(page_w / 3, page_h - 4, page_w / 3, 4, stroke=0, fill=1)
        c.setFillColor(orange); c.rect(2 * page_w / 3, page_h - 4, page_w / 3, 4, stroke=0, fill=1)

        if not self._try_logo(c, 16 * mm, page_h - 36 * mm, 65 * mm, 24 * mm):
            c.setFillColor(navy); c.setFont("Helvetica-Bold", 22); c.drawString(18 * mm, page_h - 25 * mm, "SER comtec")

        c.setFillColor(navy); c.setFont("Helvetica-Bold", 22); c.drawString(86 * mm, page_h - 19 * mm, "ORÇAMENTO")
        c.setFillColor(gray); c.setFont("Helvetica", 8); c.drawString(86 * mm, page_h - 25 * mm, "Proposta comercial SER Comunicação")

        top_y = page_h - 48 * mm
        self._draw_text_box(c, 86 * mm, top_y, 42 * mm, 18 * mm, "Nº do documento", quote.document_number, blue)
        self._draw_text_box(c, 131 * mm, top_y, 32 * mm, 18 * mm, "Data", datetime.now().strftime("%d/%m/%Y"), magenta)
        self._draw_text_box(c, 166 * mm, top_y, 29 * mm, 18 * mm, "Status", "APROVADO", orange)

        c.setStrokeColor(navy); c.rect(16 * mm, page_h - 70 * mm, 179 * mm, 16 * mm, stroke=1, fill=0)
        c.setFillColor(navy); c.setFont("Helvetica-Bold", 7.5); c.drawString(19 * mm, page_h - 59 * mm, "SER COMERCIO E SERVIÇOS")
        c.setFont("Helvetica", 7); c.setFillColor(gray); c.drawString(19 * mm, page_h - 65 * mm, "CNPJ: 28.296.513/0001-97")
        c.setFillColor(magenta); c.setFont("Helvetica-Bold", 7); c.drawString(86 * mm, page_h - 59 * mm, "Rua 9, 10 - Novo Oriente - Maracanaú - CE")
        c.setFillColor(gray); c.setFont("Helvetica", 7); c.drawString(86 * mm, page_h - 65 * mm, "atendimento@sercomunicacao.com.br")
        c.setFillColor(orange); c.setFont("Helvetica-Bold", 7); c.drawString(157 * mm, page_h - 59 * mm, "WHATSAPP")
        c.setFillColor(gray); c.setFont("Helvetica", 7); c.drawString(157 * mm, page_h - 65 * mm, "85 99867-2296 / 99166-5259")

        section_y = page_h - 108 * mm
        self._draw_text_box(
            c, 16 * mm, section_y, 88 * mm, 32 * mm, "1. Dados do cliente",
            f"NOME: {quote.client_name}\nRAZÃO SOCIAL: Não informado\nCPF / CNPJ: Não informado\nCONTATO: {quote.whatsapp}\nE-MAIL: Não informado\nENDEREÇO: Não informado", blue,
        )
        self._draw_text_box(
            c, 108 * mm, section_y, 87 * mm, 32 * mm, "2. Dados da proposta",
            f"VALIDADE: {quote.validity}\nENTREGA: Não informado\nATENDIMENTO: SER CREATIVE\nPRODUÇÃO: Não informado\nPAGAMENTO: {quote.payment_method}\nARQUIVO RECEBIDO: Não informado", magenta,
        )

        table_top = page_h - 120 * mm
        purple = colors.HexColor("#6A40FF")
        c.setFillColor(purple); c.setFont("Helvetica-Bold", 9); c.drawString(16 * mm, table_top, "3. ITENS / RESUMO FINANCEIRO")
        c.setStrokeColor(purple); c.line(16 * mm, table_top - 3, 195 * mm, table_top - 3)
        y = table_top - 14 * mm
        c.setFillColor(navy); c.rect(16 * mm, y, 179 * mm, 11 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 7)
        c.drawString(19 * mm, y + 4 * mm, "ITEM / DESCRIÇÃO")
        c.drawString(104 * mm, y + 4 * mm, "MEDIDAS")
        c.drawString(130 * mm, y + 4 * mm, "QTD.")
        c.drawString(148 * mm, y + 4 * mm, "UNITÁRIO")
        c.drawRightString(192 * mm, y + 4 * mm, "SUBTOTAL")
        row_y = y - 12 * mm
        c.setFillColor(light); c.rect(16 * mm, row_y, 179 * mm, 12 * mm, stroke=0, fill=1)
        c.setFillColor(navy); c.setFont("Helvetica-Bold", 7.5); c.drawString(19 * mm, row_y + 4.5 * mm, quote.product_name.upper()[:52])
        c.setFont("Helvetica", 7); c.drawString(104 * mm, row_y + 4.5 * mm, f"{quote.width_m.normalize()} x {quote.height_m.normalize()} m")
        c.drawString(130 * mm, row_y + 4.5 * mm, f"{quote.quantity} un")
        c.drawString(148 * mm, row_y + 4.5 * mm, _money(quote.unit_price))
        c.setFont("Helvetica-Bold", 7.5); c.drawRightString(192 * mm, row_y + 4.5 * mm, _money(quote.subtotal))

        totals_y = row_y - 28 * mm
        box_w = 44.75 * mm
        labels = [
            (blue, "SUBTOTAL", _money(quote.subtotal)),
            (purple, "DESCONTO", "- " + _money(quote.discount)),
            (magenta, "ENTREGA / INSTALAÇÃO", _money(quote.delivery_installation)),
            (orange, "VALOR TOTAL", _money(quote.total)),
        ]
        for i, (stroke, title, value) in enumerate(labels):
            x = 16 * mm + i * box_w
            c.setFillColor(navy if i == 3 else colors.white)
            c.rect(x, totals_y, box_w, 18 * mm, stroke=0, fill=1)
            c.setStrokeColor(stroke); c.rect(x, totals_y, box_w, 18 * mm, stroke=1, fill=0)
            c.setFillColor(colors.white if i == 3 else stroke); c.setFont("Helvetica-Bold", 6.5); c.drawString(x + 5, totals_y + 12 * mm, title)
            c.setFillColor(colors.white if i == 3 else navy); c.setFont("Helvetica-Bold", 11); c.drawString(x + 5, totals_y + 5 * mm, value)

        info_y = totals_y - 32 * mm
        self._draw_text_box(c, 16 * mm, info_y, 88 * mm, 24 * mm, "4. Observações", "Nenhuma informação adicional.", blue)
        self._draw_text_box(c, 108 * mm, info_y, 87 * mm, 24 * mm, "Condições e orientações", "Prazo de produção contado após aprovação da arte e confirmação do pagamento. Alterações posteriores podem gerar revisão de prazo e valor.", magenta)

        approval_y = info_y - 34 * mm
        self._draw_text_box(c, 16 * mm, approval_y, 55 * mm, 24 * mm, "5. Forma de pagamento", quote.payment_method, blue)
        self._draw_text_box(c, 76 * mm, approval_y, 57 * mm, 24 * mm, "Condição", "Conforme negociação comercial.", magenta)
        self._draw_text_box(c, 138 * mm, approval_y, 57 * mm, 24 * mm, "Fluxo após aprovação", "Após aprovação do cliente, o atendimento segue conforme as condições comerciais acordadas.", orange)

        c.setStrokeColor(colors.HexColor("#DCE4EE")); c.line(16 * mm, 18 * mm, 195 * mm, 18 * mm)
        c.setFillColor(magenta); c.setFont("Helvetica-Bold", 7); c.drawString(16 * mm, 11 * mm, "SER")
        c.setFillColor(gray); c.setFont("Helvetica", 7); c.drawString(24 * mm, 11 * mm, "Comunicação Inteligente - qualidade, agilidade e precisão.")
        c.setFillColor(blue); c.drawRightString(195 * mm, 11 * mm, "sercomunicacao.com.br")
        c.save()
        return path


class CommercialCoordinator:
    def __init__(self, db_path: str = "data/hakham.db") -> None:
        load_dotenv()
        self.catalog = CommercialCatalog()
        self.parser = QuoteParser(self.catalog)
        self.store = QuoteStore(db_path)
        self.pdf = QuotePDF(os.getenv("HAKHAM_QUOTES_DIR", "data/commercial/quotes"))

    @staticmethod
    def is_quote_request(message: str) -> bool:
        return bool(QUOTE_INTENT_RE.search(message))

    @staticmethod
    def is_approval(message: str) -> bool:
        return bool(APPROVAL_RE.match(message.strip()))

    @staticmethod
    def _message_id(result: dict[str, Any]) -> str | None:
        root = result.get("result") if isinstance(result.get("result"), dict) else result
        if not isinstance(root, dict):
            return None
        key = root.get("key")
        if isinstance(key, dict) and key.get("id"):
            return str(key["id"])
        for field in ("id", "messageId"):
            if root.get(field):
                return str(root[field])
        return None

    @staticmethod
    def preview(quote: QuoteDraft) -> str:
        width_cm = (quote.width_m * 100).quantize(Decimal("0.01")).normalize()
        height_cm = (quote.height_m * 100).quantize(Decimal("0.01")).normalize()
        return (
            f"ORÇAMENTO {quote.document_number}\n\n"
            f"Cliente: {quote.client_name}\n"
            f"WhatsApp: {quote.whatsapp}\n\n"
            f"{quote.quantity}x {quote.product_name}\n"
            f"Medida: {width_cm} x {height_cm} cm\n"
            f"Área unitária: {quote.area_unit_m2.normalize()} m²\n"
            f"Área total: {quote.area_total_m2.normalize()} m²\n"
            f"Valor unitário: {_money(quote.unit_price)}\n"
            f"Subtotal: {_money(quote.subtotal)}\n"
            f"Desconto: {_money(quote.discount)}\n"
            f"Entrega/instalação: não incluída ({_money(quote.delivery_installation)})\n"
            f"TOTAL: {_money(quote.total)}\n\n"
            f"Forma de pagamento: {quote.payment_method}\n"
            f"Validade: {quote.validity}\n\n"
            "Ach, revise o orçamento. Se estiver correto, responda exatamente: pode enviar."
        )

    def _send(self, quote: QuoteDraft) -> str:
        pdf_path = self.pdf.generate(quote)
        encoded = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
        caption = (
            f"Olá, {quote.client_name}! Segue o orçamento {quote.document_number} solicitado. "
            "Qualquer dúvida, estamos à disposição."
        )
        try:
            result = ToolGateway().execute(
                "whatsapp.send_document",
                {
                    "number": quote.whatsapp,
                    "media_base64": encoded,
                    "filename": pdf_path.name,
                    "caption": caption,
                    "mimetype": "application/pdf",
                },
                approved=True,
            )
        except Exception as exc:
            return (
                f"Ach, gerei o PDF {quote.document_number}, mas o envio pelo WhatsApp falhou: {exc}. "
                "O orçamento continua aguardando aprovação para uma nova tentativa, sem gerar outro número."
            )
        message_id = self._message_id(result)
        self.store.mark_sent(quote.id, pdf_path=str(pdf_path), message_id=message_id)
        suffix = f" · ID {message_id}" if message_id else ""
        return (
            f"Enviado, Ach. O orçamento {quote.document_number} foi gerado em PDF e aceito pela Evolution para "
            f"{quote.client_name} no WhatsApp {quote.whatsapp}{suffix}."
        )

    def handle(self, message: str, *, session_id: str = "default") -> str | None:
        text = message.strip()
        if self.is_approval(text):
            quote = self.store.latest_pending(session_id)
            if quote is None:
                return None
            return self._send(quote)

        if not self.is_quote_request(text):
            return None

        parsed, missing = self.parser.parse(text)
        if parsed is None:
            return (
                "Ach, consigo montar o orçamento, mas faltam estes dados: " + ", ".join(missing) + ". "
                "Exemplo: Hakham, faça um orçamento para Rafaela de 3 banners 120x80cm WhatsApp 5585988104302."
            )

        product_info = self.catalog.data["products"][parsed.product_key]
        if bool(product_info.get("requires_finish")) and not re.search(r"\b(ilh[oó]s|banner|acabamento)\b", text, re.I):
            return "Ach, antes de calcular preciso do acabamento da lona, por exemplo tipo banner ou ilhós. Não vou acrescentar custo de acabamento sem regra cadastrada."

        quote = self.store.create(session_id, parsed, product_info, self.catalog.rules)
        return self.preview(quote)
