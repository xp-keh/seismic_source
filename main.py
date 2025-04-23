from fastapi import FastAPI
from dotenv import load_dotenv 
from config.utils import get_env_value
from producer.kafka import Producer
from producer.seismic_streamer import SeismicSeedLinkClient
import threading

load_dotenv()

def start_seismic_stream(seedlink_host: str, kafka_broker: str, kafka_topic: str) -> None:
    producer = Producer(kafka_broker=kafka_broker, kafka_topic=kafka_topic)
    producer.create_instance()

    client = SeismicSeedLinkClient(kafka_producer=producer)
    client.select_streams(*[(s["network"], s["station"], s["location"], s["channel"]) for s in STATIONS]) # type: ignore
    client.run(seedlink_host)  # type: ignore

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

kafka_broker = get_env_value('KAFKA_BROKER')
kafka_topic = get_env_value('KAFKA_TOPIC')
seedlink_host = get_env_value('SEEDLINK_HOST')

# Create a thread for seismic stream
t_seismic = threading.Thread(
    target=start_seismic_stream,
    args=(seedlink_host, kafka_broker, kafka_topic),
    daemon=True
)

t_seismic.start()
