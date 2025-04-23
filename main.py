from fastapi import FastAPI
import threading
from producer.kafka import SeismicSeedLinkClient
from producer.station_metadata import STATIONS
from config.utils import get_env_value
import logging

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

logger.info(f"Stations to be used: {STATIONS}")

def stream_data_to_kafka():
    logger.info("[🔧] stream_data_to_kafka called.")
    kafka_broker = get_env_value('KAFKA_BROKER')
    kafka_topic = get_env_value('KAFKA_TOPIC')
    seedlink_host = get_env_value('SEEDLINK_HOST')

    seismic_client = SeismicSeedLinkClient(
        seedlink_host=seedlink_host, # type: ignore
        kafka_broker=kafka_broker, # type: ignore
        kafka_topic=kafka_topic, # type: ignore
        stations=STATIONS
    )
    
    seismic_client.create_instance()
    seismic_client.run()

@app.on_event("startup")
def start_seedlink_thread():
    stream_thread = threading.Thread(target=stream_data_to_kafka, daemon=True)
    stream_thread.start()
    logger.info("Started SeedLink client thread 🚀")
