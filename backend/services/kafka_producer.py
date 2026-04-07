"""
Apache Kafka Event Streaming
Event-Driven Resume Verification Architecture
"""

from typing import Dict, Any, Optional, Callable, List
from pydantic import BaseModel
from enum import Enum
from datetime import UTC, datetime
from logging import getLogger
import json
import os
from functools import lru_cache
import asyncio
from uuid import uuid4

from utils.time_utils import utc_now

logger = getLogger(__name__)


class EventType(str, Enum):
    """Resume verification event types"""
    
    RESUME_UPLOADED = "resume_uploaded"
    RESUME_PARSING_STARTED = "resume_parsing_started"
    RESUME_PARSED = "resume_parsed"
    AI_VERIFICATION_STARTED = "ai_verification_started"
    AI_VERIFICATION_COMPLETED = "ai_verification_completed"
    PLAGIARISM_CHECK_COMPLETED = "plagiarism_check_completed"
    BLOCKCHAIN_WRITE_STARTED = "blockchain_write_started"
    BLOCKCHAIN_RECORD_WRITTEN = "blockchain_record_written"
    VERIFICATION_FAILED = "verification_failed"


class Event(BaseModel):
    """Base event structure"""
    
    event_type: EventType
    event_id: str = None
    resume_id: str
    user_id: str
    timestamp: datetime = None
    data: Dict[str, Any]
    correlation_id: str = None
    
    def __init__(self, **kwargs):
        """Initialize event with defaults"""
        if 'event_id' not in kwargs:
            kwargs['event_id'] = str(uuid4())
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = utc_now()
        if 'correlation_id' not in kwargs:
            kwargs['correlation_id'] = str(uuid4())
        super().__init__(**kwargs)
    
    def to_json(self) -> str:
        """Serialize event to JSON"""
        return self.model_dump_json(default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Deserialize event from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class KafkaProducer:
    """
    Kafka Producer
    Publishes events to Kafka topics
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        try:
            from kafka import KafkaProducer as _KafkaProducer
            
            self.producer = _KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(","),
                value_serializer=lambda v: v.encode('utf-8') if isinstance(v, str) else v
            )
            
            logger.info(f"Kafka producer initialized: {bootstrap_servers}")
        except ImportError:
            logger.error("kafka-python not installed")
            raise
        except Exception as e:
            logger.error(f"Kafka producer initialization error: {str(e)}")
            raise
    
    def publish_event(
        self,
        topic: str,
        event: Event,
        key: str = None
    ) -> None:
        """
        Publish event to Kafka topic
        
        Args:
            topic: Kafka topic name
            event: Event to publish
            key: Message key (optional)
        """
        try:
            message = event.to_json()
            
            self.producer.send(
                topic,
                value=message,
                key=key.encode() if key else None
            )
            
            logger.info(f"Event published: {event.event_type} to {topic}")
        except Exception as e:
            logger.error(f"Event publish error: {str(e)}")
            raise
    
    def publish_batch(
        self,
        topic: str,
        events: List[Event]
    ) -> None:
        """Publish multiple events"""
        for event in events:
            self.publish_event(topic, event)
        
        self.producer.flush()
        logger.info(f"Batch publish complete: {len(events)} events to {topic}")
    
    def close(self) -> None:
        """Close producer"""
        self.producer.close()
        logger.info("Kafka producer closed")


class KafkaConsumer:
    """
    Kafka Consumer
    Consumes events from Kafka topics
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "resume-verification-consumer"
    ):
        """
        Initialize Kafka consumer
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            group_id: Consumer group ID
        """
        try:
            from kafka import KafkaConsumer as _KafkaConsumer
            
            self.consumer = _KafkaConsumer(
                bootstrap_servers=bootstrap_servers.split(","),
                group_id=group_id,
                value_deserializer=lambda m: m.decode('utf-8'),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            
            logger.info(f"Kafka consumer initialized: {group_id}")
        except ImportError:
            logger.error("kafka-python not installed")
            raise
        except Exception as e:
            logger.error(f"Kafka consumer initialization error: {str(e)}")
            raise
    
    def subscribe(self, topics: List[str]) -> None:
        """Subscribe to topics"""
        self.consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")
    
    def consume(self, timeout_ms: int = 1000) -> Optional[Event]:
        """
        Consume single event
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Event or None if no message
        """
        messages = self.consumer.poll(timeout_ms=timeout_ms)
        
        if not messages:
            return None
        
        for topic_partition, records in messages.items():
            for record in records:
                try:
                    return Event.from_json(record.value)
                except Exception as e:
                    logger.error(f"Event deserialization error: {str(e)}")
                    continue
        
        return None
    
    def consume_batch(
        self,
        batch_size: int = 10,
        timeout_ms: int = 1000
    ) -> List[Event]:
        """Consume batch of events"""
        events = []
        
        for _ in range(batch_size):
            event = self.consume(timeout_ms)
            if event:
                events.append(event)
            else:
                break
        
        return events
    
    def close(self) -> None:
        """Close consumer"""
        self.consumer.close()
        logger.info("Kafka consumer closed")


class EventBus:
    """
    Event Bus
    Central event publishing/subscribing system
    """
    
    # Topic mapping
    TOPICS = {
        EventType.RESUME_UPLOADED: "resume-upload-topic",
        EventType.AI_VERIFICATION_STARTED: "verification-started-topic",
        EventType.AI_VERIFICATION_COMPLETED: "verification-completed-topic",
        EventType.BLOCKCHAIN_WRITE_STARTED: "blockchain-started-topic",
        EventType.BLOCKCHAIN_RECORD_WRITTEN: "blockchain-completed-topic",
        EventType.VERIFICATION_FAILED: "verification-failed-topic"
    }
    
    def __init__(self, bootstrap_servers: str = None):
        """
        Initialize event bus
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092"
        )
        
        self.producer = KafkaProducer(self.bootstrap_servers)
        self.handlers: Dict[EventType, List[Callable]] = {}
    
    def publish(self, event: Event) -> None:
        """
        Publish event
        
        Args:
            event: Event to publish
        """
        topic = self.TOPICS.get(event.event_type, "default-topic")
        self.producer.publish_event(topic, event, key=event.resume_id)
        logger.info(f"Event published: {event.event_type}")
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable
    ) -> None:
        """
        Subscribe to event type
        
        Args:
            event_type: Event type to subscribe to
            handler: Callback function (async or sync)
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        logger.info(f"Handler registered for {event_type}")
    
    async def handle_event(self, event: Event) -> None:
        """
        Handle event with registered handlers
        
        Args:
            event: Event to handle
        """
        handlers = self.handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                    
            except Exception as e:
                logger.error(f"Event handler error: {str(e)}")
    
    def close(self) -> None:
        """Close event bus"""
        self.producer.close()


# Event schemas for different event types

class ResumeUploadedEvent(Event):
    """Resume uploaded event"""
    
    class Data(BaseModel):
        filename: str
        file_size_mb: float
        content_type: str
    
    def __init__(self, resume_id: str, user_id: str, data: Data):
        super().__init__(
            event_type=EventType.RESUME_UPLOADED,
            resume_id=resume_id,
            user_id=user_id,
            data=data.model_dump()
        )


class AIVerificationCompletedEvent(Event):
    """AI verification completed event"""
    
    class Data(BaseModel):
        verification_score: float
        verified: bool
        confidence: float
        processing_time_seconds: float
    
    def __init__(self, resume_id: str, user_id: str, data: Data):
        super().__init__(
            event_type=EventType.AI_VERIFICATION_COMPLETED,
            resume_id=resume_id,
            user_id=user_id,
            data=data.model_dump()
        )


class BlockchainRecordWrittenEvent(Event):
    """Blockchain record written event"""
    
    class Data(BaseModel):
        transaction_hash: str
        block_number: int
        timestamp: str
        contract_address: str
    
    def __init__(self, resume_id: str, user_id: str, data: Data):
        super().__init__(
            event_type=EventType.BLOCKCHAIN_RECORD_WRITTEN,
            resume_id=resume_id,
            user_id=user_id,
            data=data.model_dump()
        )


@lru_cache()
def get_event_bus() -> EventBus:
    """Get event bus singleton"""
    return EventBus()

