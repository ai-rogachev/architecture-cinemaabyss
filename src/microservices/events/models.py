"""
Pydantic models for CinemaAbyss Events Service
Based on the API specification schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class MovieEvent(BaseModel):
    """Model for movie events"""
    movie_id: int = Field(..., description="Идентификатор фильма", example=1)
    title: str = Field(..., description="Название фильма", example="Inception")
    action: str = Field(..., description="Действие с фильмом", example="viewed")
    user_id: Optional[int] = Field(None, description="Идентификатор пользователя (опционально)", example=1)
    rating: Optional[float] = Field(None, description="Рейтинг (опционально)", example=8.5)
    genres: Optional[List[str]] = Field(None, description="Жанры фильма (опционально)", example=["Sci-Fi", "Action"])
    description: Optional[str] = Field(None, description="Описание фильма (опционально)", example="A mind-bending thriller")

    class Config:
        schema_extra = {
            "example": {
                "movie_id": 1,
                "title": "Inception",
                "action": "viewed",
                "user_id": 1,
                "rating": 8.5,
                "genres": ["Sci-Fi", "Action"],
                "description": "A mind-bending thriller"
            }
        }


class UserEvent(BaseModel):
    """Model for user events"""
    user_id: int = Field(..., description="Идентификатор пользователя", example=1)
    username: Optional[str] = Field(None, description="Имя пользователя (опционально)", example="john_doe")
    email: Optional[str] = Field(None, description="Email пользователя (опционально)", example="john.doe@example.com")
    action: str = Field(..., description="Действие пользователя", example="registered")
    timestamp: Optional[str] = Field(None, description="Время события", example="2023-01-15T14:30:00Z")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "action": "registered",
                "timestamp": "2023-01-15T14:30:00Z"
            }
        }


class PaymentEvent(BaseModel):
    """Model for payment events"""
    payment_id: int = Field(..., description="Идентификатор платежа", example=1)
    user_id: int = Field(..., description="Идентификатор пользователя", example=1)
    amount: float = Field(..., description="Сумма платежа", example=9.99)
    status: str = Field(..., description="Статус платежа", example="completed")
    timestamp: Optional[str] = Field(None, description="Время платежа", example="2023-01-15T14:30:00Z")
    method_type: Optional[str] = Field(None, description="Тип метода оплаты (опционально)", example="credit_card")

    class Config:
        schema_extra = {
            "example": {
                "payment_id": 1,
                "user_id": 1,
                "amount": 9.99,
                "status": "completed",
                "timestamp": "2023-01-15T14:30:00Z",
                "method_type": "credit_card"
            }
        }


class Event(BaseModel):
    """Base event model"""
    id: str = Field(..., description="Уникальный идентификатор события", example="movie-1-viewed")
    type: str = Field(..., description="Тип события", example="movie")
    timestamp: str = Field(..., description="Время события", example="2023-01-15T14:30:00Z")
    payload: Dict[str, Any] = Field(..., description="Полезная нагрузка события (зависит от типа события)")

    class Config:
        schema_extra = {
            "example": {
                "id": "movie-1-viewed",
                "type": "movie",
                "timestamp": "2023-01-15T14:30:00Z",
                "payload": {
                    "movie_id": 1,
                    "title": "Inception",
                    "action": "viewed",
                    "user_id": 1
                }
            }
        }


class EventResponse(BaseModel):
    """Response model for event creation"""
    status: str = Field(..., description="Статус операции", example="success")
    partition: int = Field(..., description="Партиция Kafka", example=0)
    offset: int = Field(..., description="Смещение в партиции Kafka", example=42)
    event: Event = Field(..., description="Созданное событие")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "partition": 0,
                "offset": 42,
                "event": {
                    "id": "movie-1-viewed",
                    "type": "movie",
                    "timestamp": "2023-01-15T14:30:00Z",
                    "payload": {
                        "movie_id": 1,
                        "title": "Inception",
                        "action": "viewed",
                        "user_id": 1
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Сообщение об ошибке", example="Internal Server Error")

    class Config:
        schema_extra = {
            "example": {
                "error": "Internal Server Error"
            }
        }


# Additional models for internal use
class KafkaEvent(BaseModel):
    """Internal model for Kafka events"""
    topic: str
    partition: int
    offset: int
    event: Event
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True


class HealthResponse(BaseModel):
    """Health check response model"""
    status: bool = Field(..., description="Статус работоспособности", example=True)

    class Config:
        schema_extra = {
            "example": {
                "status": True
            }
        }
