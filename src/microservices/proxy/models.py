from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class Movie(BaseModel):
    id: int
    title: str
    description: str
    genres: List[str]
    rating: float


class MovieInput(BaseModel):
    title: str
    description: str
    genres: List[str]
    rating: float


# Event models
class Event(BaseModel):
    id: str
    type: str
    timestamp: datetime
    payload: dict


class MovieEvent(BaseModel):
    movie_id: int
    title: str
    action: str
    user_id: Optional[int] = None
    rating: Optional[float] = None
    genres: Optional[List[str]] = None
    description: Optional[str] = None


class UserEvent(BaseModel):
    user_id: int
    action: str
    timestamp: datetime
    username: Optional[str] = None
    email: Optional[str] = None


class PaymentEvent(BaseModel):
    payment_id: int
    user_id: int
    amount: float
    status: str
    timestamp: datetime
    method_type: Optional[str] = None


class EventResponse(BaseModel):
    status: str
    partition: int
    offset: int
    event: Event
