import os


class Settings:
    APP_NAME = "Floresis OpsPilot AI"
    APP_VERSION = "0.2.0"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./opspilot.db"
    )


settings = Settings()