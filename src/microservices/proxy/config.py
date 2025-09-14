import os
from typing import Optional


class Settings:
    def __init__(self):
        self.port: int = int(os.getenv("PORT", "8000"))
        self.monolith_url: str = os.getenv("MONOLITH_URL", "http://monolith:8080")
        self.movies_service_url: str = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
        self.events_service_url: str = os.getenv("EVENTS_SERVICE_URL", "http://events-service:8082")
        self.gradual_migration: bool = os.getenv("GRADUAL_MIGRATION", "false").lower() == "true"
        self.movies_migration_percent: int = int(os.getenv("MOVIES_MIGRATION_PERCENT", "0"))


settings = Settings()
