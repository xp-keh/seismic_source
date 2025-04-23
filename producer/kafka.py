from obspy.clients.seedlink import EasySeedLinkClient
from obspy.clients.seedlink.slpacket import SLPacket
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
from datetime import datetime
from typing import List

from config.logger import Logger

class SeismicSeedLinkClient(EasySeedLinkClient):
    def __init__(self, seedlink_host: str, kafka_broker: str, kafka_topic: str, stations: List[dict]):
        self.logger.info(" [*] Initializing SeismicSeedLinkClient...")
        super().__init__(server_url=seedlink_host)
        self._kafka_server = kafka_broker
        self._kafka_topic = kafka_topic
        self._stations = stations
        self._instance = None
        self.logger = Logger().setup_logger(service_name='seismic_producer')
        self.select_streams()

    def create_instance(self) -> KafkaProducer:
        self.logger.info(" [*] Starting Kafka producer...")

        for attempt in range(5):
            try:
                self._instance = KafkaProducer(
                    bootstrap_servers=self._kafka_server,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    api_version=(0, 11, 5)
                )
                self.logger.info(" [*] Kafka producer connected.")
                return self._instance
            except KafkaError as e:
                self.logger.error(f" [!] Attempt {attempt + 1} - Kafka connection failed: {e}")
                time.sleep(5)

        raise RuntimeError(" [X] Could not connect to Kafka after multiple attempts.")

    def select_streams(self):
        if not self._stations:
            self.logger.warning(" [!] No stations defined to subscribe to.")
            return
        
        for station in self._stations:
            self.logger.info(f" [*] Selecting {station['network']}.{station['station']}:{station.get('channel', 'HHZ')}")
            self.select_stream(
                net=station["network"],
                station=station["station"],
                selector=station.get("channel", "HHZ")
            )

    def run(self):
        self.logger.info(" [*] Starting seismic data stream...")
        while True:
            data = self.conn.collect()
            arrive_time = datetime.utcnow()
            process_start_time = time.time()

            if data == SLPacket.SLTERMINATE:
                self.logger.warning(" [!] SeedLink connection terminated.")
                break
            elif data == SLPacket.SLERROR:
                self.logger.error(" [X] SeedLink connection error.")
                continue

            if isinstance(data, SLPacket):
                trace = data.get_trace()
                if trace.stats.channel in ["BHZ", "BHN", "BHE", "HHZ"]:
                    self.on_data_arrive(trace, arrive_time, process_start_time)

    def on_data_arrive(self, trace, arrive_time, process_start_time):
        msg = self._map_values(trace, arrive_time, process_start_time)
        try:
            self._instance.send(self._kafka_topic, msg) # type: ignore
            self.logger.info(f" [>] Sent trace from {trace.stats.station}.{trace.stats.channel}")
        except KafkaError as e:
            self.logger.error(f" [X] Failed to send message to Kafka: {e}")

    def _map_values(self, trace, arrive_time, process_start_time):
        return {
            "station": trace.stats.station,
            "network": trace.stats.network,
            "channel": trace.stats.channel,
            "starttime": trace.stats.starttime.isoformat(),
            "sampling_rate": trace.stats.sampling_rate,
            "data": trace.data.tolist(),
            "raw_produce_dt": int(arrive_time.timestamp() * 1_000_000),
            "process_start_time": process_start_time
        }
