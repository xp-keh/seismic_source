from fastapi import FastAPI, BackgroundTasks
from stream.manager import streamManager
from stream.client import StreamMode
from obspy import UTCDateTime
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

SOURCE_MSEED = "20090118_064750.mseed"

load_dotenv()
app = FastAPI()
PORT = os.getenv("PORT", "8003")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/live")
def live(background_task: BackgroundTasks):
    background_task.add_task(streamManager.start, StreamMode.LIVE)
    return "ok"

if __name__ == "__main__":
    config = uvicorn.Config(
        "main:app", port=int(PORT), log_level="info", host="0.0.0.0"
    )
    server = uvicorn.Server(config)
    server.run()
