from .prometheus_metric import start_prometheus_server
from .producer import KafkaProducer, kafkaProducer
from .fdsnws_client import FdsnwsClient
from .seedlink_client import SeedLinkClient
from .const import StreamMode


class StreamManager:
    def __init__(
        self, producer: KafkaProducer, fdsnws_server: str, seedlink_server: str
    ):
        start_prometheus_server()
        self.producer = producer
        self.fdsnws_server = fdsnws_server
        self.seedlink_server = seedlink_server
        self.fdsnws = FdsnwsClient(self.producer, base_url=self.fdsnws_server)
        self.seedlink = SeedLinkClient(self.producer, server_url=self.seedlink_server)

    def start(self, mode: StreamMode, *args, **kwargs):
        if self.fdsnws.blocked:
            print("Blocked")
            return
        if mode == StreamMode.PLAYBACK:
            try:
                if self.producer.current_mode == StreamMode.LIVE:
                    self.seedlink.stop_streaming()
                self.producer.current_mode = StreamMode.PLAYBACK
                self.fdsnws.start_streaming(*args, **kwargs)
            except Exception as err:
                print(err)
            finally:
                self.fdsnws.stop_streaming()
                self.producer.current_mode = StreamMode.IDLE

        if mode == StreamMode.FILE:
            try:
                self.producer.current_mode = StreamMode.FILE
                # self.fileclient.startStreaming(*args, **kwargs)
            except Exception as err:
                print(err)
            finally:
                self.producer.current_mode = StreamMode.IDLE

        elif mode == StreamMode.LIVE and self.producer.current_mode == StreamMode.IDLE:
            self.producer.current_mode = StreamMode.LIVE
            self.seedlink.start_streaming()

        elif mode == StreamMode.IDLE:  # stop live mode
            self.producer.current_mode = StreamMode.IDLE
            self.seedlink.stop_streaming()
        print(self.producer.current_mode)


streamManager = StreamManager(
    producer=kafkaProducer,
    fdsnws_server="GEOFON",
    seedlink_server="geofon.gfz-potsdam.de:18000",
)
