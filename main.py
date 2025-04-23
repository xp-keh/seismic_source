from fastapi import FastAPI
import threading
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from producer.seismic_streamer import start_seismic_stream
from config.utils import get_env_value

load_dotenv()

KAFKA_BROKER = get_env_value("KAFKA_BROKER")
KAFKA_TOPIC = get_env_value("KAFKA_TOPIC")
SEEDLINK_HOST = get_env_value("SEEDLINK_HOST")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

streaming_thread = threading.Thread(
    target=start_seismic_stream,
    args=(SEEDLINK_HOST, KAFKA_BROKER, KAFKA_TOPIC),
    daemon=True
)
streaming_thread.start()