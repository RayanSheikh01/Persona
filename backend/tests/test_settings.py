from persona.settings import Settings


def _isolated(monkeypatch, **env):
    for k in ("HF_TOKEN", "HF_CHAT_MODEL", "HF_EMBED_MODEL",
              "PERSONA_API_KEY", "DATABASE_URL", "PERSONA_LOG_LEVEL"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return Settings(_env_file=None)


def test_env_vars_populate_settings(monkeypatch):
    settings = _isolated(
        monkeypatch,
        HF_TOKEN="hf_test",
        PERSONA_API_KEY="secret",
        DATABASE_URL="sqlite:///data/x.db",
    )
    assert settings.hf_token == "hf_test"
    assert settings.persona_api_key == "secret"
    assert settings.database_url == "sqlite:///data/x.db"


def test_defaults_apply_when_unset(monkeypatch):
    settings = _isolated(monkeypatch)
    assert settings.hf_chat_model == "meta-llama/Llama-3.1-8B-Instruct"
    assert settings.hf_embed_model == "sentence-transformers/all-mpnet-base-v2"
    assert settings.persona_log_level == "INFO"


def test_get_settings_returns_settings(monkeypatch):
    settings = _isolated(monkeypatch)
    assert isinstance(settings, Settings)
    assert settings.hf_token == "hf_replace_me"
    assert settings.working_buffer_turns == 20
    assert settings.working_summarize_stride == 10
    assert settings.procedural_maxx_rules == 20
    assert settings.dedup_threshold == 0.92
    assert settings.supersede_threshold == 0.85

    