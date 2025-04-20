import time
from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Optional, Any

from .producer import KafkaProducer
from utils.redis_client import RedisSingleton
from .const import StreamMode
from obspy import Trace

class StreamClient(ABC):
    def __init__(self, mode: StreamMode, producer: KafkaProducer):
        self.mode: StreamMode = mode
        self.producer = producer
        redis = RedisSingleton()
        stats: str = redis.r.get("ENABLED_STATION_CODES")
        print(redis.r.get("ENABLED_STATION_CODES"))
        self.stations: set = set(stats.split(","))

    @abstractmethod
    def start_streaming(self, start_time: Optional[Any], end_time: Optional[Any]):
        pass

    @abstractmethod
    def stop_streaming(self):
        pass

    @staticmethod
    def _map_values(trace: Trace, arrive_time, process_start_time):
        msg = {
            "type":"trace",
            "network": trace.stats.network,
            "station": trace.stats.station,
            "channel": trace.stats.channel,
            "location": trace.stats.location,
            "starttime": str(trace.stats.starttime),
            "endtime": str(trace.stats.endtime),
            "delta": trace.stats.delta,
            "npts": trace.stats.npts,
            "calib": trace.stats.calib,
            "data": trace.data.tolist(),
            "len": len(trace.data.tolist()),
            "sampling_rate": trace.stats.sampling_rate,
            "eews_producer_time":[arrive_time.isoformat(), datetime.now(UTC).isoformat()],
            "published_at": time.time(),
            "process_start_time": process_start_time
        }
        return msg
