from confluent_kafka.admin import AdminClient, NewTopic

from src.shared.config import settings

admin = AdminClient({'bootstrap.servers': settings.kafka_broker})

topic_list = [NewTopic(settings.kafka_email_send_topic_name, settings.kafka_email_send_topic_partitions, 1)]
fs = admin.create_topics(topic_list)

for topic, f in fs.items():
    try:
        f.result()
        print(f"Topic {topic} created")
    except Exception as e:
        print(f"Failed to create topic {topic}: {e}")