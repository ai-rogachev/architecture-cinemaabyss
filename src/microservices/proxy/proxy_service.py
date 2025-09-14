import httpx
import random
from typing import List, Optional, Union
from fastapi import HTTPException
from .models import Movie, MovieInput, User, UserInput, Payment, PaymentInput, Subscription, SubscriptionInput
from .config import settings


class ProxyService:
    def __init__(self):
        self.monolith_url = settings.monolith_url
        self.movies_service_url = settings.movies_service_url
        self.events_service_url = settings.events_service_url
        self.gradual_migration = settings.gradual_migration
        self.movies_migration_percent = settings.movies_migration_percent

    def _should_use_microservice(self) -> bool:
        """Определяет, использовать ли микросервис на основе фиче-флага и процента миграции"""
        if not self.gradual_migration:
            return False
        
        # Генерируем случайное число от 1 до 100
        random_percent = random.randint(1, 100)
        return random_percent <= self.movies_migration_percent

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> dict:
        """Выполняет HTTP запрос к указанному URL"""
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = await client.post(url, **kwargs)
                else:
                    raise HTTPException(status_code=405, detail="Method not allowed")
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {e.response.text}")
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

    async def get_movies(self, movie_id: Optional[int] = None) -> List[Movie]:
        """Получает список фильмов или конкретный фильм по ID"""
        if self._should_use_microservice():
            # Используем микросервис movies
            if movie_id:
                url = f"{self.movies_service_url}/api/movies?id={movie_id}"
            else:
                url = f"{self.movies_service_url}/api/movies"
        else:
            # Используем монолит
            if movie_id:
                url = f"{self.monolith_url}/api/movies?id={movie_id}"
            else:
                url = f"{self.monolith_url}/api/movies"
        
        data = await self._make_request(url)
        
        # Если запрашивается конкретный фильм, возвращаем его как список из одного элемента
        if movie_id:
            return [Movie(**data)]
        else:
            return [Movie(**movie) for movie in data]

    async def create_movie(self, movie: MovieInput) -> Movie:
        """Создает новый фильм"""
        if self._should_use_microservice():
            # Используем микросервис movies
            url = f"{self.movies_service_url}/api/movies"
        else:
            # Используем монолит
            url = f"{self.monolith_url}/api/movies"
        
        data = await self._make_request(url, method="POST", json=movie.dict())
        return Movie(**data)

    async def proxy_to_events(self, path: str, method: str = "GET", **kwargs) -> dict:
        """Проксирует запросы к сервису events"""
        url = f"{self.events_service_url}{path}"
        return await self._make_request(url, method=method, **kwargs)

    async def proxy_to_monolith(self, path: str, method: str = "GET", **kwargs) -> dict:
        """Проксирует запросы к монолиту (для всех остальных API)"""
        url = f"{self.monolith_url}{path}"
        return await self._make_request(url, method=method, **kwargs)
