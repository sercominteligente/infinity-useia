from pathlib import Path


def test_hakham_reference_webp_is_complete() -> None:
    path = Path("assets/hakham-reference.webp")
    data = path.read_bytes()

    assert len(data) > 10_000
    assert data[:4] == b"RIFF"
    assert data[8:12] == b"WEBP"

    declared_size = int.from_bytes(data[4:8], "little") + 8
    assert declared_size == len(data)
