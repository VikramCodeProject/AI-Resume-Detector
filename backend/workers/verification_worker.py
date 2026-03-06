"""
Verification Worker
Consumes verification events and processes resumes
"""

import asyncio
from logging import getLogger
from typing import Optional
import json
from datetime import datetime

from services.kafka_producer import (
    KafkaConsumer, EventBus, EventType, Event,
    AIVerificationCompletedEvent
)

logger = getLogger(__name__)


class VerificationWorker:
    """
    Verification Worker
    Processes resume_uploaded events and runs verification pipeline
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize verification worker
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        self.consumer = KafkaConsumer(bootstrap_servers)
        self.event_bus = EventBus(bootstrap_servers)
        self.is_running = False
    
    async def start(self) -> None:
        """Start worker"""
        self.is_running = True
        self.consumer.subscribe([
            "resume-upload-topic",
            "verification-started-topic"
        ])
        
        logger.info("Verification worker started")
        
        while self.is_running:
            try:
                event = self.consumer.consume(timeout_ms=1000)
                
                if event:
                    await self.process_event(event)
                    
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(1)
    
    async def process_event(self, event: Event) -> None:
        """
        Process verification event
        
        Args:
            event: Event to process
        """
        logger.info(f"Processing event: {event.event_type}")
        
        try:
            if event.event_type == EventType.RESUME_UPLOADED:
                await self.handle_resume_uploaded(event)
            elif event.event_type == EventType.RESUME_PARSED:
                await self.handle_resume_parsed(event)
                
        except Exception as e:
            logger.error(f"Event processing error: {str(e)}")
            # Publish failure event
            await self.publish_failure_event(event, str(e))
    
    async def handle_resume_uploaded(self, event: Event) -> None:
        """
        Handle resume upload event
        Start verification pipeline
        
        Args:
            event: Upload event
        """
        resume_id = event.resume_id
        user_id = event.user_id
        
        logger.info(f"Starting verification for resume {resume_id}")
        
        # Simulate verification pipeline
        # In production, call actual ML services
        import random
        verification_score = random.uniform(0.6, 0.99)
        processing_time = random.uniform(2.0, 8.0)
        
        # Publish completion event
        verification_event = AIVerificationCompletedEvent(
            resume_id=resume_id,
            user_id=user_id,
            data=AIVerificationCompletedEvent.Data(
                verification_score=verification_score,
                verified=verification_score >= 0.75,
                confidence=0.95,
                processing_time_seconds=processing_time
            )
        )
        
        self.event_bus.publish(verification_event)
        logger.info(f"Verification completed for resume {resume_id}: {verification_score:.2f}")
    
    async def handle_resume_parsed(self, event: Event) -> None:
        """Handle resume parsed event"""
        resume_id = event.resume_id
        
        # Run ML verification
        logger.info(f"Running ML verification for {resume_id}")
        
        # Simulate ML processing
        await asyncio.sleep(0.5)
        
        logger.info(f"ML verification completed for {resume_id}")
    
    async def publish_failure_event(self, original_event: Event, error: str) -> None:
        """
        Publish failure event
        
        Args:
            original_event: Original event
            error: Error message
        """
        failure_event = Event(
            event_type=EventType.VERIFICATION_FAILED,
            resume_id=original_event.resume_id,
            user_id=original_event.user_id,
            data={
                "error": error,
                "original_event_type": original_event.event_type.value,
                "correlation_id": original_event.correlation_id
            },
            correlation_id=original_event.correlation_id
        )
        
        self.event_bus.publish(failure_event)
    
    def stop(self) -> None:
        """Stop worker"""
        self.is_running = False
        self.consumer.close()
        self.event_bus.close()
        logger.info("Verification worker stopped")


async def main():
    """Main worker function"""
    worker = VerificationWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
