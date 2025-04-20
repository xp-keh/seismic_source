import time

from .client import StreamClient
from .producer import KafkaProducer
from obspy.clients.fdsn import Client
import logging
import json
from datetime import datetime, UTC
from .const import StreamMode
from utils.redis_client import RedisSingleton

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FdsnwsClient(StreamClient, Client):
    def __init__(self, producer: KafkaProducer, base_url: str):
        StreamClient.__init__(self, mode=StreamMode.LIVE, producer=producer)
        Client.__init__(self, base_url=base_url)
        self.stats = None
        self.blocked = False

    def start_streaming(self, start_time, end_time):
        logging.info("Starting FDSN Client...")
        self.stats: str = RedisSingleton().r.get("ENABLED_STATION_CODES")
        self.stations = set(self.stats.split(","))
        
        self.producer.start_trace()
        self.blocked = True
        result = []
        res = self._bulk(start_time, end_time)
        arrive_time = datetime.now(UTC)
        for trace in res:
            msg = self._map_values(trace, arrive_time=arrive_time, process_start_time=time.time())
            self.producer.produce_message(json.dumps(msg), msg["station"], StreamMode.PLAYBACK)
        return result
    
    def stop_streaming(self): # currently not supported to cancel midrequest
        logging.info("Stopping playback...")
        self.blocked = False
        self.producer.stop_trace()

    def _bulk(self, start_time, end_time):
        bulk = [("GE", station, "*", "BH?", start_time, end_time)
                for station in self.stations]
        result = self.get_waveforms_bulk(bulk=bulk)
        return result
