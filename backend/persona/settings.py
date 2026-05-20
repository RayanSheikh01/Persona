from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    hf_token: str = Field(default="hf_replace_me")
    hf_chat_model: str = Field(default="meta-llama/Llama-3.1-8B-Instruct")
    hf_embed_model: str = Field(default="sentence-transformers/all-mpnet-base-v2")
    persona_api_key: str = Field(default="local-dev-shared-secret")
    database_url: str = Field(default="sqlite:///data/persona.db")
    persona_log_level: str = Field(default="INFO")
    working_buffer_turns: int = Field(default=20)
    working_summarize_stride: int = Field(default=10)
    procedural_max_rules: int = Field(default=20)
    dedup_threshold: float = Field(default=0.92)
    supersede_threshold: float = Field(default=0.85)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")



def get_settings() -> Settings:
    return Settings()