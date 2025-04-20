import os
from dotenv import load_dotenv
from collections.abc import Callable
from confluent_kafka import Producer
from typing import Any, Dict
from typing import Optional
import logging
import pickle
import json
from .const import StreamMode
from config.redis_client import RedisSingleton

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', "172.20.0.77:9093")
if not BOOTSTRAP_SERVERS:
    raise Exception("BOOTSTRAP_SERVER env is required")
TOPIC_NAME = os.getenv('TOPIC_NAME', "query")
if not TOPIC_NAME:
    raise Exception("Topic name env is required")

DEFAULT_PRODUCER_CONFIG = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
}


class KafkaProducer:
    def __init__(
        self,
        topic_name: str,
        value_serializer: Optional[Callable[[object], bytes]] = None,
        extra_config: Optional[Dict] = None,
    ):
        self.stations = []
        logging.debug("Create producer")

        if extra_config is None:
            extra_config = {}

        self.producer = Producer({**DEFAULT_PRODUCER_CONFIG, **extra_config})
        try:
            self.partitions = len(
                self.producer.list_topics(TOPIC_NAME).topics.get(TOPIC_NAME).partitions
            )
        except Exception as e:
            print(e)
            self.partitions = 3

        self.topic_name = topic_name
        self.current_mode = StreamMode.IDLE

        self.value_serializer = value_serializer
        if self.value_serializer is None:
            self.value_serializer = pickle.dumps

        logging.debug("Finish creating producer")

    def start_trace(self):
        stats: str = RedisSingleton().r.get("ENABLED_STATION_CODES")
        self.stations = set(stats.split(","))
        for i in range(0, self.partitions):
            self.producer.produce(
                self.topic_name,
                value=self.value_serializer(json.dumps({"type": "start"})),
                partition=i,
                key="start",
            )
        self.producer.flush()
        print("=" * 20, "Start Trace", "=" * 20)

    def stop_trace(self):
        for i in range(0, self.partitions):
            self.producer.produce(
                self.topic_name,
                value=self.value_serializer(json.dumps({"type": "stop"})),
                partition=i,
                key="stop",
            )
        self.producer.flush()
        print("=" * 20, "Stop Trace", "=" * 20)

    def produce_message(
        self,
        value,
        key: Optional[Any] = None,
        mode=StreamMode.IDLE,
    ):
        if mode == self.current_mode and key in self.stations:
            self.producer.produce(
                self.topic_name,
                value=self.value_serializer(value),
                key=key,
            )

        self.producer.flush()

    def log_on_kafka_message_delivery(self, error: Optional[str], message):
        if error is not None:
            logging.error(
                f"Failed to produce message: {message.value()}, topic: {self.topic_name} error: {error}"
            )

        else:
            logging.debug(
                f"Successfully produced message: {message.value()}, topic: {self.topic_name}"
            )

    def get_on_delivery_function(
        self, extra_function: Optional[Callable[[str, str], None]]
    ):
        if extra_function is None:
            return self.log_on_kafka_message_delivery

        return lambda error, message: (
            self.log_on_kafka_message_delivery(error, message),
            extra_function(error, message),
        )


kafkaProducer = KafkaProducer(TOPIC_NAME)
