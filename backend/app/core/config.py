from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://financemacro:changeme_in_prod@db:5432/financemacro"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    hermes_api_key: str = "changeme_hermes_key"
    secret_key: str = "changeme_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
