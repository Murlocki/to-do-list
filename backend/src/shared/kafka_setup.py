

import asyncio

from confluent_kafka.admin import AdminClient, NewTopic

from src.shared.config import settings


async def recreate_kafka(topic_configs: dict[str, int], replication_factor: int = 1):
    admin = AdminClient({'bootstrap.servers': settings.kafka_broker})

    existing_topics = admin.list_topics(timeout=10).topics
    topics_to_delete = [t for t in topic_configs if t in existing_topics]

    if topics_to_delete:
        print(f"Initiating deletion of: {topics_to_delete}")
        fs = admin.delete_topics(topics_to_delete)
        for topic, f in fs.items():
            try:
                f.result()
                print(f"Deletion initiated for topic: {topic}")
            except Exception as e:
                print(f"Failed to delete topic {topic}: {e}")

        # Ждём пока Kafka полностью удалит топики
        for _ in range(10):  # до 10 попыток
            current_topics = admin.list_topics(timeout=10).topics
            if all(t not in current_topics for t in topics_to_delete):
                break
            print("Waiting for topic deletion...")
            await asyncio.sleep(2)
        else:
            print("Timeout: Kafka did not delete topics in time.")
            return

    # Создание новых топиков
    topic_list = [NewTopic(t, num_partitions=p, replication_factor=replication_factor)
                  for t, p in topic_configs.items()]
    fs = admin.create_topics(topic_list)
    for topic, f in fs.items():
        try:
            f.result()
            print(f"Topic {topic} created")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}")

if __name__ == "__main__":
    asyncio.run(recreate_kafka({
        settings.kafka_email_send_topic_name: int(settings.kafka_email_send_topic_partitions),
        settings.kafka_task_remind_topic_name: int(settings.kafka_task_remind_topic_partitions),
    }))