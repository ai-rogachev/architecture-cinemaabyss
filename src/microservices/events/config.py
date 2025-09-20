import os
from typing import List


class Settings:
    def __init__(self):
        # Port configuration - use environment variable or default to 8082
        self.port: int = int(os.getenv("PORT", "8082"))
        self.host: str = os.getenv("HOST", "0.0.0.0")
        
        self.kafka_bootstrap_server: str = os.getenv("KAFKA_BROKERS", '127.0.0.1:9092')
        
        self.kafka_topics: dict = {
            "movie_events": "movie-events",
            "user_events": "user-events", 
            "payment_events": "payment-events"
        }
        
        # Logging settings
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Application settings
        self.app_name: str = "CinemaAbyss Events Service"
        self.app_version: str = "1.0.0"
        self.app_description: str = "Service for handling events and pushing them to Kafka"
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_log_levels}")
    
    def __str__(self):
        return f"Settings(port={self.port}, host={self.host}, log_level={self.log_level})"


# Global settings instance
settings = Settings()
