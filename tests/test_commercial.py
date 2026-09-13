from decimal import Decimal

from hakham.commercial import CommercialCatalog, CommercialCoordinator, QuotePDF, QuoteParser, QuoteStore


def test_banner_quote_parses_and_calculates(tmp_path) -> None:
    catalog = CommercialCatalog("data/commercial_catalog.json")
    parser = QuoteParser(catalog)
    message = "Hakham faça um orçamento para Rafaela de 3 banners 120x80cm WhatsApp 5585988104302"
    parsed, missing = parser.parse(message)
    assert missing == []
    assert parsed is not None
    assert parsed.client_name == "Rafaela"
    assert parsed.whatsapp == "5585988104302"
    assert parsed.product_key == "banner"
    assert parsed.quantity == 3
    assert parsed.width_m == Decimal("1.2")
    assert parsed.height_m == Decimal("0.8")

    store = QuoteStore(str(tmp_path / "hakham.db"))
    quote = store.create("default", parsed, catalog.data["products"]["banner"], catalog.rules)
    assert quote.area_unit_m2 == Decimal("0.9600")
    assert quote.area_total_m2 == Decimal("2.8800")
    assert quote.price_per_m2 == Decimal("80.0000")
    assert quote.unit_price == Decimal("76.80")
    assert quote.subtotal == Decimal("230.40")
    assert quote.total == Decimal("230.40")
    assert quote.status == "awaiting_approval"


def test_pdf_generation_uses_quote_snapshot(tmp_path) -> None:
    catalog = CommercialCatalog("data/commercial_catalog.json")
    parsed, missing = QuoteParser(catalog).parse(
        "Hakham faça um orçamento para Rafaela de 3 banners 120x80cm WhatsApp 5585988104302"
    )
    assert not missing and parsed is not None
    quote = QuoteStore(str(tmp_path / "hakham.db")).create(
        "default", parsed, catalog.data["products"]["banner"], catalog.rules
    )
    path = QuotePDF(str(tmp_path / "quotes")).generate(quote)
    payload = path.read_bytes()
    assert payload.startswith(b"%PDF-")
    assert len(payload) > 1500
    assert quote.document_number in path.name


def test_only_explicit_short_approval_triggers_send_intent() -> None:
    assert CommercialCoordinator.is_approval("pode enviar") is True
    assert CommercialCoordinator.is_approval("Pode mandar!") is True
    assert CommercialCoordinator.is_approval("pode enviar depois") is False
    assert CommercialCoordinator.is_approval("não pode enviar") is False
