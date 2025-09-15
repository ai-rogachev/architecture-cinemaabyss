import os
from typing import Optional


class Settings:
    def __init__(self):
        # Port configuration - use environment variable or default to 8000
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Service URLs - use environment variables with sensible defaults
        self.monolith_url: str = os.getenv("MONOLITH_URL", "http://monolith:8080")
        self.movies_service_url: str = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
        self.events_service_url: str = os.getenv("EVENTS_SERVICE_URL", "http://events-service:8082")
        
        # Feature flags for gradual migration
        self.gradual_migration: bool = os.getenv("GRADUAL_MIGRATION", "false").lower() == "true"
        self.movies_migration_percent: int = int(os.getenv("MOVIES_MIGRATION_PERCENT", "0"))
        
        # Logging configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.enable_proxy_logging: bool = os.getenv("ENABLE_PROXY_LOGGING", "true").lower() == "true"
        self.log_target_destination: bool = os.getenv("LOG_TARGET_DESTINATION", "true").lower() == "true"
        
        # Validate migration percentage
        if not 0 <= self.movies_migration_percent <= 100:
            raise ValueError("MOVIES_MIGRATION_PERCENT must be between 0 and 100")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_log_levels}")
    
    def __str__(self):
        return f"Settings(port={self.port}, gradual_migration={self.gradual_migration}, migration_percent={self.movies_migration_percent}, log_level={self.log_level})"


# Global settings instance
settings = Settings()
