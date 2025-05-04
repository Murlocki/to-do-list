import asyncio
import json

from aiokafka import AIOKafkaProducer

from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

async def send_to_kafka(message):
    """Асинхронная отправка в Kafka с улучшенной обработкой ошибок"""
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_broker,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        await producer.start()
        await producer.send('task_remind', message)
        await producer.flush()  # Гарантируем отправку
        logger.info("Successfully sent to Kafka: %s", message)
    except Exception as e:
        logger.error("Kafka send error: %s", str(e))
        raise
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(send_to_kafka({"task_remind": 1}))