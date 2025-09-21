"""
CinemaAbyss Events Service
FastAPI application for handling events and pushing them to Kafka
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException

from models import MovieEvent, UserEvent, PaymentEvent, EventResponse
from config import settings

from mvp_kafka import consume_events, init_kafka_consumers, init_kafka_producer, send_to_kafka

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Service for handling events and pushing them to Kafka",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka connections on startup"""
    logger.info("Starting Events Service...")
    
    global kafka_producer, kafka_consumer
    try:
        kafka_producer = init_kafka_producer()
        kafka_consumer = init_kafka_consumers()
        logger.info("Kafka producer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        raise
    
    logger.info("Events Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Kafka connections on shutdown"""
    logger.info("Shutting down Events Service...")
    
    global kafka_producer, kafka_consumer
    if kafka_producer:
        kafka_producer.close()
    if kafka_consumer:
        # Close all consumers in the dictionary
        for consumer_name, consumer in kafka_consumer.items():
            try:
                consumer.close()
                logger.info(f"Closed consumer: {consumer_name}")
            except Exception as e:
                logger.error(f"Error closing consumer {consumer_name}: {e}")
    
    logger.info("Events Service shutdown complete")


@app.get("/api/events/health", response_model=Dict[str, bool])
async def get_events_service_health():
    """
    Проверка работоспособности микросервиса событий
    """
    logger.info("Health check requested")
    return {"status": True}


@app.post("/api/events/movie", response_model=EventResponse, status_code=201)
async def create_movie_event(event: MovieEvent):
    """
    Создание события фильма
    """
    logger.info(f"Creating movie event: {event.title} - {event.action}")
    
    try:
        # Generate event ID and timestamp
        event_id = f"movie-{event.movie_id}-{event.action}-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create event payload
        event_payload = {
            "id": event_id,
            "type": "movie",
            "timestamp": timestamp,
            "payload": {
                "movie_id": event.movie_id,
                "title": event.title,
                "action": event.action,
                "user_id": event.user_id,
                "rating": event.rating,
                "genres": event.genres,
                "description": event.description
            }
        }
        
        kafka_result = await send_to_kafka(kafka_producer, "movie-events", event_payload)
        logger.info(f"Movie event sent to Kafka: {kafka_result}")
        
        if kafka_result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=f"Failed to send event to Kafka: {kafka_result.get('error')}")
        
        # Try to consume the event we just sent
        response = await consume_events(kafka_consumer['movie_events'])
        logger.info(f"Movie event received from Kafka: {response}")
        
        # If no messages were consumed, that's okay - the event was still sent successfully
        if response.status == "no_messages":
            # Return a success response indicating the event was sent but not immediately consumed
            return EventResponse(
                status="success",
                partition=kafka_result.get('partition', 0),
                offset=kafka_result.get('offset', 0),
                event=event_payload
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating movie event: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/events/user", response_model=EventResponse, status_code=201)
async def create_user_event(event: UserEvent):
    """
    Создание события пользователя
    """
    logger.info(f"Creating user event: user {event.user_id} - {event.action}")
    
    try:
        # Generate event ID and timestamp
        event_id = f"user-{event.user_id}-{event.action}-{uuid.uuid4().hex[:8]}"
        timestamp = event.timestamp or datetime.utcnow().isoformat() + "Z"
        
        # Create event payload
        event_payload = {
            "id": event_id,
            "type": "user",
            "timestamp": timestamp,
            "payload": {
                "user_id": event.user_id,
                "username": event.username,
                "email": event.email,
                "action": event.action,
                "timestamp": timestamp
            }
        }
        
        kafka_result = await send_to_kafka(kafka_producer, "user-events", event_payload)
        logger.info(f"User event sent to Kafka: {kafka_result}")
        
        if kafka_result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=f"Failed to send event to Kafka: {kafka_result.get('error')}")
        
        # Try to consume the event we just sent
        response = await consume_events(kafka_consumer['user_events'])
        logger.info(f"User event received from Kafka: {response}")
        
        # If no messages were consumed, that's okay - the event was still sent successfully
        if response.status == "no_messages":
            # Return a success response indicating the event was sent but not immediately consumed
            return EventResponse(
                status="success",
                partition=kafka_result.get('partition', 0),
                offset=kafka_result.get('offset', 0),
                event=event_payload
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating user event: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/events/payment", response_model=EventResponse, status_code=201)
async def create_payment_event(event: PaymentEvent):
    """
    Создание события платежа
    """
    logger.info(f"Creating payment event: payment {event.payment_id} - {event.status}")
    
    try:
        # Generate event ID and timestamp
        event_id = f"payment-{event.payment_id}-{event.status}-{uuid.uuid4().hex[:8]}"
        timestamp = event.timestamp or datetime.utcnow().isoformat() + "Z"
        
        # Create event payload
        event_payload = {
            "id": event_id,
            "type": "payment",
            "timestamp": timestamp,
            "payload": {
                "payment_id": event.payment_id,
                "user_id": event.user_id,
                "amount": event.amount,
                "status": event.status,
                "timestamp": timestamp,
                "method_type": event.method_type
            }
        }
        
        kafka_result = await send_to_kafka(kafka_producer, "payment-events", event_payload)
        logger.info(f"Payment event sent to Kafka: {kafka_result}")
        
        if kafka_result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=f"Failed to send event to Kafka: {kafka_result.get('error')}")
        
        # Try to consume the event we just sent
        response = await consume_events(kafka_consumer['payment_events'])
        logger.info(f"Payment event received from Kafka: {response}")
        
        # If no messages were consumed, that's okay - the event was still sent successfully
        if response.status == "no_messages":
            # Return a success response indicating the event was sent but not immediately consumed
            return EventResponse(
                status="success",
                partition=kafka_result.get('partition', 0),
                offset=kafka_result.get('offset', 0),
                event=event_payload
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating payment event: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
