from hakham.web_v6_readable import CONTROL_CENTER_HTML, TYPOGRAPHY_FLOOR_CSS


def test_readability_floor_is_injected() -> None:
    assert "HAKHAM readability floor" in CONTROL_CENTER_HTML
    assert "font-size:11px!important" in TYPOGRAPHY_FLOOR_CSS


def test_high_frequency_operational_text_is_lifted() -> None:
    for selector in (
        ".navbtn",
        ".engine-pill",
        ".eyebrow",
        ".avatar-state",
        ".modebtn",
        ".agent .role",
        ".tool .tstate",
        ".perm",
        ".bubble strong",
    ):
        assert selector in TYPOGRAPHY_FLOOR_CSS


def test_operational_text_uses_12px_where_space_allows() -> None:
    assert ".chatrow textarea" in TYPOGRAPHY_FLOOR_CSS
    assert "font-size:12px" in TYPOGRAPHY_FLOOR_CSS
