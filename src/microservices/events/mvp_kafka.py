from kafka import KafkaConsumer, KafkaProducer
from models import EventResponse
import json
import time
import asyncio
from config import settings

def init_kafka_producer():
    return KafkaProducer(bootstrap_servers=settings.kafka_bootstrap_server,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def init_kafka_consumers():
    # Base consumer configuration
    base_config = {
        'bootstrap_servers': settings.kafka_bootstrap_server,
        'auto_offset_reset': 'earliest',  # Start from earliest messages to catch all events
        'enable_auto_commit': True,     # Auto-commit offsets
        'auto_commit_interval_ms': 1000, # Commit every 1 second
        'session_timeout_ms': 30000,    # 30 seconds session timeout
        'heartbeat_interval_ms': 10000, # 10 seconds heartbeat
        'max_poll_interval_ms': 300000, # 5 minutes max poll interval
        'fetch_min_bytes': 1,           # Don't wait for more data
        'fetch_max_wait_ms': 500,       # Wait max 500ms for data
        'consumer_timeout_ms': 1000,    # 1 second timeout for consumer operations
    }
    
    # Create consumers with UNIQUE group IDs (timestamp-based) to avoid rebalancing
    timestamp = int(time.time())
    consumers = {
        'movie_events': KafkaConsumer(
            settings.kafka_topics['movie_events'], 
            group_id=f'movie-events-group-{timestamp}',
            **base_config
        ),
        'user_events': KafkaConsumer(
            settings.kafka_topics['user_events'], 
            group_id=f'user-events-group-{timestamp}',
            **base_config
        ),
        'payment_events': KafkaConsumer(
            settings.kafka_topics['payment_events'], 
            group_id=f'payment-events-group-{timestamp}',
            **base_config
        )
    }
    return consumers

async def send_to_kafka(producer, topic, message):
    """
    Send message to Kafka topic and return metadata
    """
    try:
        # Send message to Kafka
        future = producer.send(topic, message)
        
        # Wait for the message to be sent and get metadata
        record_metadata = future.get(timeout=10)
        
        return {
            'status': 'success',
            'topic': record_metadata.topic,
            'partition': record_metadata.partition,
            'offset': record_metadata.offset,
            'timestamp': record_metadata.timestamp
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


async def consume_events(consumer):
    """
    Consume one event from Kafka consumer and return EventResponse
    """
    try:
        # Get one message from the consumer with timeout
        message = next(consumer)
        
        # Parse the message value (it's already JSON from our producer)
        event_data = json.loads(message.value.decode('utf-8'))
        
        # Create EventResponse with actual Kafka metadata
        response = EventResponse(
            status="success",
            partition=message.partition,
            offset=message.offset,
            event=event_data
        )
        
        return response
        
    except StopIteration:
        # No messages available - this is normal when no new messages
        return EventResponse(
            status="no_messages",
            partition=0,
            offset=0,
            event={"message": "No new messages available in topic"}
        )
    except json.JSONDecodeError as e:
        # Error parsing JSON
        return EventResponse(
            status="error",
            partition=0,
            offset=0,
            event={"error": f"Failed to parse message JSON: {str(e)}"}
        )
    except Exception as e:
        # Error consuming message
        return EventResponse(
            status="error",
            partition=0,
            offset=0,
            event={"error": f"Failed to consume message: {str(e)}"}
        )
