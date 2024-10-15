from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    algorithm: str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()