from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
from obspy.core import UTCDateTime
from producer.kafka import Producer
from producer.station_metadata import STATIONS

class SeismicSeedLinkClient(EasySeedLinkClient):
    def __init__(self, kafka_producer: Producer):
        super().__init__() # type: ignore
        self.kafka_producer = kafka_producer

    def on_data(self, trace):
        data_dict = {
            "station": trace.stats.station,
            "network": trace.stats.network,
            "channel": trace.stats.channel,
            "starttime": trace.stats.starttime.isoformat(),
            "sampling_rate": trace.stats.sampling_rate,
            "data": trace.data.tolist()
        }
        self.kafka_producer.send(data_dict)

def start_seismic_stream(seedlink_host: str, kafka_broker: str, kafka_topic: str):
    producer = Producer(kafka_broker, kafka_topic)
    producer.create_instance()

    client = SeismicSeedLinkClient(kafka_producer=producer)
    client.select_streams(*[(s["network"], s["station"], s["location"], s["channel"]) for s in STATIONS]) # type: ignore
    client.run(seedlink_host) # type: ignore
