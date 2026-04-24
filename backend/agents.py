"""
SATELLITE ALPHA — Multi-agent hedge fund in a box.

Each agent is a distinct Claude call with a specialized system prompt.
They run in parallel where possible, then a synthesizer agent reconciles.
"""

from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "claude-opus-4-7"
client = AsyncAnthropic()


# ──────────────────────────────────────────────────────────────────────────
# AGENT 1 — VISION AGENT: Counts cars in parking lot images
# ──────────────────────────────────────────────────────────────────────────

VISION_SYSTEM = """You are a satellite imagery analyst specializing in retail foot traffic.
Your job: examine aerial/satellite images of parking lots and count vehicles accurately.

For each image, output STRICT JSON:
{
  "car_count": <integer>,
  "lot_capacity_estimate": <integer>,
  "fill_rate": <float 0-1>,
  "weather_visible": "<clear|overcast|snow|rain|unclear>",
  "time_of_day_estimate": "<morning|midday|afternoon|evening|unclear>",
  "anomalies": ["<construction>", "<event>", ...],
  "confidence": <float 0-1>
}

Count carefully. A single row of cars is a line of roughly-rectangular shapes.
If the lot is sparse, count every car. If dense, estimate by sections.
Return ONLY the JSON, no preamble."""


async def vision_agent(image_paths: list[str], dates: list[str]) -> list[dict]:
    """Analyze each parking lot image. Runs all in parallel."""

    async def analyze_one(img_path: str, date: str) -> dict:
        with open(img_path, "rb") as f:
            img_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

        # Infer media type from extension
        ext = Path(img_path).suffix.lower()
        media_type = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
        }.get(ext, "image/jpeg")

        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=VISION_SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Image captured on {date}. Count the cars and return JSON.",
                    },
                ],
            }],
        )

        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        result["date"] = date
        result["image_path"] = img_path
        return result

    tasks = [analyze_one(p, d) for p, d in zip(image_paths, dates)]
    return await asyncio.gather(*tasks)


# ──────────────────────────────────────────────────────────────────────────
# AGENT 2 — TRENDS AGENT: Analyzes Google Trends for ticker/brand
# ──────────────────────────────────────────────────────────────────────────

TRENDS_SYSTEM = """You are a digital demand analyst. Given Google search trend data for
a retailer brand, identify the directional signal for consumer interest vs prior periods.

Output STRICT JSON:
{
  "trend_direction": "<rising|stable|declining>",
  "yoy_change_pct": <float>,
  "qoq_change_pct": <float>,
  "signal_strength": <float 0-1>,
  "notable_spikes": ["<description>", ...],
  "interpretation": "<one sentence>"
}

Return ONLY the JSON."""


async def trends_agent(ticker: str, brand: str, trends_data: dict) -> dict:
    """Interpret Google Trends data for the brand."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=TRENDS_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Ticker: {ticker}
Brand: {brand}
Google Trends data (weekly search interest, scale 0-100):
{json.dumps(trends_data, indent=2)}

Analyze this and return JSON.""",
        }],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────
# AGENT 3 — CONTEXT AGENT: Pulls fundamentals and street expectations
# ──────────────────────────────────────────────────────────────────────────

CONTEXT_SYSTEM = """You are an equity research analyst. Given recent fundamentals and
analyst consensus for a ticker, summarize the setup going into earnings.

Output STRICT JSON:
{
  "consensus_ss_sales_growth_pct": <float>,
  "consensus_eps": <float>,
  "recent_price_performance_90d_pct": <float>,
  "implied_move_pct": <float>,
  "bull_points": ["<point>", ...],
  "bear_points": ["<point>", ...],
  "setup": "<long|neutral|short>"
}

Return ONLY the JSON."""


async def context_agent(ticker: str, fundamentals: dict) -> dict:
    """Analyze fundamentals + street setup."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=CONTEXT_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Ticker: {ticker}
Fundamentals and analyst data:
{json.dumps(fundamentals, indent=2)}

Return JSON analysis.""",
        }],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────
# AGENT 4 — SYNTHESIZER: Reconciles all signals into a trade thesis
# ──────────────────────────────────────────────────────────────────────────

SYNTHESIZER_SYSTEM = """You are a portfolio manager at an alternative-data hedge fund.
You receive signals from three analysts:
  1. A vision analyst who counted cars in parking lots across time
  2. A digital demand analyst interpreting Google search trends
  3. An equity research analyst with fundamentals and street expectations

Your job: reconcile these into a single trade thesis with REAL conviction.

Consider:
- Do the alternative data signals (cars + trends) AGREE with each other?
- Do they DIVERGE from what Wall Street expects? (This is where alpha lives.)
- What is the asymmetric setup — how much upside on a beat vs downside on a miss?

Output STRICT JSON:
{
  "ticker": "<ticker>",
  "thesis": "<2-3 sentence trade thesis in portfolio-manager voice>",
  "direction": "<LONG|SHORT|NEUTRAL>",
  "conviction": "<LOW|MEDIUM|HIGH>",
  "predicted_ss_sales_growth_pct": <float>,
  "vs_consensus_bps": <integer — positive = we're above street>,
  "expected_stock_move_on_beat_pct": <float>,
  "expected_stock_move_on_miss_pct": <float>,
  "key_risks": ["<risk>", ...],
  "signal_agreement": "<all agree|mixed|diverging>",
  "alpha_source": "<which signal is doing the most work>",
  "citations": [
     {"signal": "vision|trends|context", "claim": "<what it told us>"},
     ...
  ]
}

Return ONLY the JSON. No preamble."""


async def synthesizer_agent(
    ticker: str,
    vision_results: list[dict],
    trends_result: dict,
    context_result: dict,
) -> dict:
    """Reconcile all signals into a trade thesis."""

    # Compute traffic delta from vision results
    if len(vision_results) >= 2:
        early = sum(r["car_count"] for r in vision_results[:len(vision_results)//2])
        late = sum(r["car_count"] for r in vision_results[len(vision_results)//2:])
        traffic_delta_pct = ((late - early) / early * 100) if early else 0
    else:
        traffic_delta_pct = 0

    vision_summary = {
        "observations": vision_results,
        "traffic_delta_pct_period_over_period": round(traffic_delta_pct, 1),
        "mean_fill_rate": round(
            sum(r["fill_rate"] for r in vision_results) / len(vision_results), 2
        ) if vision_results else 0,
    }

    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYNTHESIZER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""TICKER: {ticker}

━━━ SIGNAL 1: PARKING LOT TRAFFIC (Vision Agent) ━━━
{json.dumps(vision_summary, indent=2)}

━━━ SIGNAL 2: DIGITAL DEMAND (Trends Agent) ━━━
{json.dumps(trends_result, indent=2)}

━━━ SIGNAL 3: FUNDAMENTALS & STREET (Context Agent) ━━━
{json.dumps(context_result, indent=2)}

Reconcile these signals and output the trade thesis JSON.""",
        }],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR — runs everything, streams progress
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Signal:
    name: str
    status: str  # "pending" | "running" | "done" | "error"
    data: Any = None


async def run_pipeline(
    ticker: str,
    brand: str,
    image_paths: list[str],
    image_dates: list[str],
    trends_data: dict,
    fundamentals: dict,
    progress_callback=None,
) -> dict:
    """Run the full multi-agent pipeline with progress streaming."""

    async def report(step: str, status: str, data=None):
        if progress_callback:
            await progress_callback({"step": step, "status": status, "data": data})

    # Stage 1: Run three analysts in PARALLEL
    await report("vision", "running")
    await report("trends", "running")
    await report("context", "running")

    vision_task = vision_agent(image_paths, image_dates)
    trends_task = trends_agent(ticker, brand, trends_data)
    context_task = context_agent(ticker, fundamentals)

    vision_results, trends_result, context_result = await asyncio.gather(
        vision_task, trends_task, context_task
    )

    await report("vision", "done", vision_results)
    await report("trends", "done", trends_result)
    await report("context", "done", context_result)

    # Stage 2: Synthesizer
    await report("synthesizer", "running")
    thesis = await synthesizer_agent(
        ticker, vision_results, trends_result, context_result
    )
    await report("synthesizer", "done", thesis)

    return {
        "ticker": ticker,
        "vision": vision_results,
        "trends": trends_result,
        "context": context_result,
        "thesis": thesis,
    }
