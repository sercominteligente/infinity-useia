from hakham.instagram_direct import InstagramDirectClient


def test_instagram_direct_loads_two_read_only_accounts(monkeypatch) -> None:
    monkeypatch.setenv("META_INSTAGRAM_SER_COMTEC_USERNAME", "ser.com.tec")
    monkeypatch.setenv("META_INSTAGRAM_SER_COMTEC_ACCOUNT_ID", "111")
    monkeypatch.setenv("META_INSTAGRAM_SER_COMTEC_ACCESS_TOKEN", "token-one")
    monkeypatch.setenv("META_INSTAGRAM_SER_VISUAL_USERNAME", "ser.com.visual")
    monkeypatch.setenv("META_INSTAGRAM_SER_VISUAL_ACCOUNT_ID", "222")
    monkeypatch.setenv("META_INSTAGRAM_SER_VISUAL_ACCESS_TOKEN", "token-two")

    client = InstagramDirectClient()
    status = client.status()

    assert status["configured"] is True
    assert status["mode"] == "instagram_login_read_only"
    usernames = {row["username"] for row in status["accounts"]}
    assert usernames == {"ser.com.tec", "ser.com.visual"}
    assert all("access_token" not in row for row in status["accounts"])


def test_instagram_direct_resolves_owned_account(monkeypatch) -> None:
    monkeypatch.setenv("META_INSTAGRAM_SER_COMTEC_USERNAME", "ser.com.tec")
    monkeypatch.setenv("META_INSTAGRAM_SER_COMTEC_ACCESS_TOKEN", "token-one")
    monkeypatch.delenv("META_INSTAGRAM_SER_VISUAL_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("META_INSTAGRAM_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("META_GRAPH_ACCESS_TOKEN", raising=False)

    client = InstagramDirectClient()
    account = client._resolve("@ser.com.tec")

    assert account is not None
    assert account.key == "ser_comtec"
    assert account.username == "ser.com.tec"
