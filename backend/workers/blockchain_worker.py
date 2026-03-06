"""
Blockchain Worker
Consumes verification events and writes to blockchain
"""

import asyncio
from logging import getLogger
from typing import Optional
import json

from services.kafka_producer import (
    KafkaConsumer, EventBus, EventType, Event,
    BlockchainRecordWrittenEvent
)

logger = getLogger(__name__)


class BlockchainWorker:
    """
    Blockchain Worker
    Processes verification events and writes to blockchain
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        blockchain_service=None
    ):
        """
        Initialize blockchain worker
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            blockchain_service: BlockchainService instance
        """
        self.consumer = KafkaConsumer(
            bootstrap_servers,
            group_id="blockchain-consumer-group"
        )
        self.event_bus = EventBus(bootstrap_servers)
        self.blockchain_service = blockchain_service
        self.is_running = False
    
    async def start(self) -> None:
        """Start worker"""
        self.is_running = True
        self.consumer.subscribe([
            "verification-completed-topic"
        ])
        
        logger.info("Blockchain worker started")
        
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
        Process verification event and write to blockchain
        
        Args:
            event: Event to process
        """
        logger.info(f"Processing blockchain event: {event.event_type}")
        
        try:
            if event.event_type == EventType.AI_VERIFICATION_COMPLETED:
                await self.write_verification_to_blockchain(event)
                
        except Exception as e:
            logger.error(f"Blockchain write error: {str(e)}")
            await self.publish_failure_event(event, str(e))
    
    async def write_verification_to_blockchain(self, event: Event) -> None:
        """
        Write verification result to blockchain
        
        Args:
            event: Verification completed event
        """
        resume_id = event.resume_id
        user_id = event.user_id
        verification_data = event.data
        
        logger.info(f"Writing verification to blockchain for {resume_id}")
        
        try:
            if self.blockchain_service:
                # Call blockchain service to write record
                tx_hash, block_number = await self.blockchain_service.write_verification(
                    resume_id=resume_id,
                    verification_score=verification_data.get("verification_score"),
                    verified=verification_data.get("verified")
                )
            else:
                # Simulate blockchain write for testing
                import hashlib
                tx_hash = hashlib.sha256(
                    f"{resume_id}{verification_data}".encode()
                ).hexdigest()
                block_number = 12345
            
            # Publish blockchain written event
            blockchain_event = BlockchainRecordWrittenEvent(
                resume_id=resume_id,
                user_id=user_id,
                data=BlockchainRecordWrittenEvent.Data(
                    transaction_hash=tx_hash,
                    block_number=block_number,
                    timestamp=str(event.timestamp),
                    contract_address="0x1234567890123456789012345678901234567890"
                )
            )
            
            self.event_bus.publish(blockchain_event)
            logger.info(f"Blockchain record written for {resume_id}: {tx_hash}")
            
        except Exception as e:
            logger.error(f"Blockchain write failed: {str(e)}")
            raise
    
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
                "error": f"Blockchain write failed: {error}",
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
        logger.info("Blockchain worker stopped")


async def main():
    """Main worker function"""
    worker = BlockchainWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
