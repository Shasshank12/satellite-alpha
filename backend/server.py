"""
FastAPI server that exposes the multi-agent pipeline as a streaming endpoint.
Frontend connects to /analyze and gets server-sent events as each agent completes.
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from agents import run_pipeline
from demo_data import get_demo_package

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "satellite-alpha online", "model": "claude-opus-4-7"}


@app.post("/analyze")
async def analyze(
    ticker: str = Form(...),
    use_demo: bool = Form(True),
):
    """Run the multi-agent pipeline. Streams progress as SSE."""

    async def event_stream():
        # Progress queue — each agent pushes updates here
        queue: asyncio.Queue = asyncio.Queue()

        async def progress(update):
            await queue.put(update)

        # Load demo package (images, trends, fundamentals for the ticker)
        demo = get_demo_package(ticker)

        # Kick off pipeline in background
        async def run():
            try:
                result = await run_pipeline(
                    ticker=ticker,
                    brand=demo["brand"],
                    image_paths=demo["image_paths"],
                    image_dates=demo["image_dates"],
                    trends_data=demo["trends_data"],
                    fundamentals=demo["fundamentals"],
                    progress_callback=progress,
                )
                await queue.put({"step": "complete", "status": "done", "data": result})
                await queue.put({"step": "__END__"})
            except Exception as e:
                await queue.put({
                    "step": "error", "status": "error", "data": str(e)
                })
                await queue.put({"step": "__END__"})

        task = asyncio.create_task(run())

        # Stream events from queue
        yield f"data: {json.dumps({'step': 'start', 'status': 'running', 'data': {'ticker': ticker, 'brand': demo['brand']}})}\n\n"

        while True:
            update = await queue.get()
            if update.get("step") == "__END__":
                break
            yield f"data: {json.dumps(update)}\n\n"

        await task

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/reveal/{ticker}")
async def reveal(ticker: str):
    """Reveal what actually happened — the mic-drop moment."""
    demo = get_demo_package(ticker)
    return demo["actual_outcome"]


# Serve demo images
app.mount(
    "/images",
    StaticFiles(directory=str(Path(__file__).parent.parent / "data" / "images")),
    name="images",
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
