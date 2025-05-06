import json

from aiokafka import AIOKafkaConsumer
from socketio import AsyncServer

from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.task_service.main import sio

logger = setup_logger(__name__)
async def consume_kafka_messages():
    consumer = AIOKafkaConsumer(
        settings.kafka_task_remind_topic_name,
        bootstrap_servers=settings.kafka_broker,
        group_id="readers",
        auto_offset_reset='latest'
    )

    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode())
                await sio.emit('task_remind', {
                    'message': data,
                    'timestamp': msg.timestamp
                }, room=f"user_{data['user']}")
            except json.JSONDecodeError:
                logger.error("Invalid JSON in Kafka message")
            except Exception as e:
                logger.error(f"Message processing failed: {str(e)}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer disconnected")