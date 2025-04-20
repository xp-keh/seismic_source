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

@app.get("/playback")
def playback(
    background_task: BackgroundTasks,
    start_time: str | None = None,
    end_time: str | None = None,
):
    if start_time is None:
        start_time = UTCDateTime("2019-12-31T18:18:28.00+07")
    if end_time is None:
        end_time = UTCDateTime(start_time) + 30 * 6
    print(start_time)
    print(end_time)
    background_task.add_task(
        streamManager.start, StreamMode.PLAYBACK, start_time, end_time
    )
    return "ok"


@app.get("/live")
def live(background_task: BackgroundTasks):
    background_task.add_task(streamManager.start, StreamMode.LIVE)
    return "ok"


@app.post("/idle")
def live(background_task: BackgroundTasks):
    background_task.add_task(streamManager.start, StreamMode.IDLE)
    return "ok"


@app.get("/file")
def live(background_task: BackgroundTasks, filename: str = SOURCE_MSEED):
    background_task.add_task(streamManager.start, StreamMode.FILE, filename)
    return "ok"

if __name__ == "__main__":
    config = uvicorn.Config(
        "main:app", port=int(PORT), log_level="info", host="0.0.0.0"
    )
    server = uvicorn.Server(config)
    server.run()
