import pytest

from hakham.voice import OpenAITTSClient, normalize_spoken_text


def test_tts_requires_api_key():
    client = OpenAITTSClient(api_key="", base_url="https://api.openai.com/v1")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        client.synthesize("Shalom, Ach")


def test_tts_rejects_empty_text():
    client = OpenAITTSClient(api_key="test", base_url="https://api.openai.com/v1")
    with pytest.raises(ValueError, match="empty"):
        client.synthesize("   ")


def test_tts_rejects_text_above_api_limit():
    client = OpenAITTSClient(api_key="test", base_url="https://api.openai.com/v1")
    with pytest.raises(ValueError, match="4096"):
        client.synthesize("x" * 4097)


def test_spoken_text_normalizes_brazilian_chat_laughter_without_touching_other_text():
    assert normalize_spoken_text("Kkkkk meu Ach, agora ficou bom") == "haha meu Ach, agora ficou bom"
    assert normalize_spoken_text("k k k bora testar") == "haha bora testar"
    assert normalize_spoken_text("HAKHAM operacional") == "HAKHAM operacional"
