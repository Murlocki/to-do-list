import asyncio
import json

from aiokafka import AIOKafkaConsumer

from src.email_service.send_functions import send_email_with_retry
from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)


async def consume():
    consumer = AIOKafkaConsumer(
        settings.kafka_email_send_topic_name,
        bootstrap_servers=settings.kafka_broker,
        group_id="email-sender",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest'
    )

    await consumer.start()
    async for msg in consumer:
        logger.info(f"Received message: {msg.value}")
        data = msg.value
        body = data.get("token", "")
        to_email = data.get("email", "")
        message_type = data.get("message_type", "")
        if to_email:
            await send_email_with_retry(message_type, f"{settings.register_link}/{body}", to_email)
        else:
            logger.error("Missing 'to' field in message")

    await consumer.stop()


async def start_consumer(consumer_count: int = settings.kafka_email_send_topic_partitions):
    """
    Start multiple consumers to process messages concurrently.
    :param consumer_count: Number of consumers to start
    """
    tasks = [consume() for _ in range(consumer_count)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(start_consumer())
