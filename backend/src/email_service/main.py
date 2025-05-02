import asyncio

from src.email_service.kafka_consumer import  start_consumer

if __name__ == "__main__":
    asyncio.run(start_consumer())



