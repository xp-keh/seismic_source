from kafka import KafkaProducer
import json

class Producer:
    def __init__(self, kafka_broker: str, kafka_topic: str):
        self.kafka_broker = kafka_broker
        self.kafka_topic = kafka_topic
        self.producer = None

    def create_instance(self):
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, message: dict):
        if self.producer is not None:
            self.producer.send(self.kafka_topic, message)
        else:
            raise Exception("Kafka producer not initialized. Call create_instance() first.")

    def flush(self):
        if self.producer:
            self.producer.flush()
