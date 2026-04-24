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

ROOT_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "wound-iq online", "model": "claude-opus-4-7"}


@app.post("/analyze")
async def analyze(
    patient_id: str = Form(...),
    use_demo: bool = Form(True),
):
    """Run the multi-agent pipeline. Streams progress as SSE."""

    async def event_stream():
        # Progress queue — each agent pushes updates here
        queue: asyncio.Queue = asyncio.Queue()

        async def progress(update):
            await queue.put(update)

        # Load demo package (images + patient context for the case)
        demo = get_demo_package(patient_id)

        # Kick off pipeline in background
        async def run():
            try:
                result = await run_pipeline(
                    patient_id=patient_id,
                    wound_type=demo["wound_type"],
                    patient_context=demo["patient_context"],
                    image_paths=demo["image_paths"],
                    image_dates=demo["image_dates"],
                    baseline_metrics=demo["baseline_metrics"],
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
        yield f"data: {json.dumps({'step': 'start', 'status': 'running', 'data': {'patient_id': patient_id, 'wound_type': demo['wound_type']}})}\n\n"

        while True:
            update = await queue.get()
            if update.get("step") == "__END__":
                break
            yield f"data: {json.dumps(update)}\n\n"

        await task

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/reveal/{patient_id}")
async def reveal(patient_id: str):
    """Reveal what actually happened — the mic-drop moment."""
    demo = get_demo_package(patient_id)
    return demo["actual_outcome"]


# Serve demo images
app.mount(
    "/images",
    StaticFiles(directory=str(ROOT_DIR / "data" / "images")),
    name="images",
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
