from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import os

from models import Movie, MovieInput, MovieEvent
from models import UserEvent, PaymentEvent, EventResponse

from proxy_service import ProxyService
from config import settings

app = FastAPI(title="CinemaAbyss Proxy Service", version="1.0.0")

# Инициализируем прокси-сервис
proxy_service = ProxyService()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return "Strangler Fig Proxy is healthy"


@app.get("/api/proxy/health")
async def proxy_health_check():
    """Health check endpoint for Kubernetes probes"""
    return "Strangler Fig Proxy is healthy"


@app.get("/api/movies", response_model=List[Movie])
async def get_movies(movie_id: Optional[int] = Query(None, description="ID of specific movie")):
    """
    Получает список всех фильмов или конкретный фильм по ID.
    Использует фиче-флаг для постепенного переключения между монолитом и микросервисом.
    """
    try:
        movies = await proxy_service.get_movies(movie_id)
        return movies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/movies", response_model=Movie, status_code=201)
async def create_movie(movie: MovieInput):
    """
    Создает новый фильм.
    Использует фиче-флаг для постепенного переключения между монолитом и микросервисом.
    """
    try:
        created_movie = await proxy_service.create_movie(movie)
        return created_movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Events API endpoints
@app.get("/api/events/health")
async def get_events_service_health():
    """Проверка работоспособности микросервиса событий"""
    try:
        result = await proxy_service.proxy_to_events("/api/events/health", method="GET")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/events/movie", response_model=EventResponse, status_code=201)
async def create_movie_event(event: MovieEvent):
    """Создание события фильма"""
    try:
        result = await proxy_service.proxy_to_events("/api/events/movie", method="POST", json=event.dict())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/events/user", response_model=EventResponse, status_code=201)
async def create_user_event(event: UserEvent):
    """Создание события пользователя"""
    try:
        result = await proxy_service.proxy_to_events("/api/events/user", method="POST", json=event.dict())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/events/payment", response_model=EventResponse, status_code=201)
async def create_payment_event(event: PaymentEvent):
    """Создание события платежа"""
    try:
        result = await proxy_service.proxy_to_events("/api/events/payment", method="POST", json=event.dict())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.api_route("/api/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_events(request: Request, path: str):
    """
    Проксирует все остальные запросы к сервису events.
    """
    try:
        # Получаем тело запроса если есть
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
        
        # Получаем query параметры
        query_params = dict(request.query_params)
        
        # Формируем полный путь
        full_path = f"/api/events/{path}"
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            full_path += f"?{query_string}"
        
        # Проксируем запрос
        kwargs = {}
        if body:
            kwargs["content"] = body
            kwargs["headers"] = {"Content-Type": "application/json"}
        
        result = await proxy_service.proxy_to_events(full_path, method=request.method, **kwargs)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_monolith(request: Request, path: str):
    """
    Проксирует все остальные запросы к монолиту.
    """
    try:
        # Получаем тело запроса если есть
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
        
        # Получаем query параметры
        query_params = dict(request.query_params)
        
        # Формируем полный путь
        full_path = f"/{path}"
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            full_path += f"?{query_string}"
        
        # Проксируем запрос
        kwargs = {}
        if body:
            kwargs["content"] = body
            kwargs["headers"] = {"Content-Type": "application/json"}
        
        result = await proxy_service.proxy_to_monolith(full_path, method=request.method, **kwargs)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False
    )
