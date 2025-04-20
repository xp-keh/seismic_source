from typing import Optional, Any

from .client import StreamClient
from .const import StreamMode
from .producer import KafkaProducer
from obspy.clients.seedlink import EasySeedLinkClient
from obspy import Trace
import json
from datetime import datetime, UTC
import time
from obspy.clients.seedlink.slpacket import SLPacket


class SeedLinkClient(StreamClient, EasySeedLinkClient):
    def __init__(self, producer: KafkaProducer, server_url: str):
        self.server_url = server_url
        StreamClient.__init__(self, mode=StreamMode.LIVE, producer=producer)
        EasySeedLinkClient.__init__(self, server_url=self.server_url)
        self.__streaming_started = False
        print("Starting new seedlink client")
        for station in self.stations:
            self.select_stream(net="GE", station=station, selector="BH?")
        print("Starting connection to seedlink server ", self.server_hostname)
        self.experiment_attempt = 0
        self.experiment_execution_times = []
        self.experiment_processed_data = []
        self.experiment_cpu_usages = []  # Add this line
        self.experiment_memory_usages = []  # Add this line

    def run(self):
        if not len(self.conn.streams):
            raise Exception(
                "No streams specified. Use select_stream() to select a stream"
            )
        self.__streaming_started = True
        # Start the collection loop
        print("Starting collection on:", datetime.now(UTC))
        while True:
            data = self.conn.collect()
            arrive_time = datetime.now(UTC)
            process_start_time = time.time()

            if data == SLPacket.SLTERMINATE:
                print("Connection terminated")
                self.on_terminate()
                break
            elif data == SLPacket.SLERROR:
                print("Connection error")
                self.on_seedlink_error()
                continue

            assert isinstance(data, SLPacket)
            packet_type = data.get_type()
            if packet_type not in (SLPacket.TYPE_SLINF, SLPacket.TYPE_SLINFT):
                trace = data.get_trace()
                if trace.stats.channel in ["BHZ", "BHN", "BHE"]:
                    self.on_data_arrive(trace, arrive_time, process_start_time)


    def start_streaming(self, start_time: Optional[Any]= None, end_time: Optional[Any]= None):
        self.producer.start_trace()
        print("-" * 20, "Streaming miniseed from seedlink server", "-" * 20)
        print('Streaming started', not self.__streaming_started)
        if not self.__streaming_started:
            self.run()

    def stop_streaming(self):
        self.producer.stop_trace()
        self.close()
        print("-" * 20, "Stopping miniseed", "-" * 20)

    def on_data_arrive(self, trace: Trace, arrive_time: datetime, process_start_time: float):
        msg = self._map_values(trace, arrive_time, process_start_time)
        self.producer.produce_message(json.dumps(msg), msg["station"], StreamMode.LIVE)