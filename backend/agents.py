"""
WOUND IQ — Multi-agent clinical decision support pipeline.

Each agent is a distinct Claude call with a specialized system prompt.
They run in stages with explicit dependencies, then a care agent synthesizes.
"""

from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from demo_data import DEMO_MODE, WOUND_PACKAGE

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = "claude-opus-4-7"
client = AsyncAnthropic()


# ──────────────────────────────────────────────────────────────────────────
# AGENT 1 — WOUND VISION AGENT
# ──────────────────────────────────────────────────────────────────────────

VISION_SYSTEM = """You are a wound imaging analyst specializing in chronic wound visual assessment.
You are clinical decision support, not a diagnosis. Your output augments — does not replace — clinician judgment.

Your task: evaluate each wound image and return STRICT JSON with this shape:
{
    "estimated_dimensions_mm": {"length": <int>, "width": <int>, "depth_estimate": "<superficial|partial-thickness|full-thickness|unable-to-assess>"},
    "tissue_composition_pct": {"granulation": <int>, "slough": <int>, "eschar": <int>, "epithelial": <int>},
    "wound_bed_color": "<red|pink|yellow|black|mixed>",
    "exudate": {"amount": "<none|minimal|moderate|heavy>", "type": "<serous|sanguinous|purulent|unclear>"},
    "periwound_skin": {"erythema_present": <bool>, "edema_present": <bool>, "maceration_present": <bool>, "redness_extent_mm": <int>},
    "infection_indicators": ["<indicator>", ...],
    "image_quality": "<good|adequate|poor>",
    "confidence": <float 0-1>,
    "notes": "<brief clinical observation>"
}

Rules:
- Keep tissue percentages clinically plausible and summing approximately to 100.
- If a field cannot be assessed from image quality/angle, still provide best estimate and mention uncertainty in notes.
- Return ONLY JSON. No markdown. No preamble."""


async def wound_vision_agent(image_paths: list[str], image_dates: list[str]) -> list[dict]:
    """Analyze each wound image. Runs all images in parallel."""

    def detect_media_type(image_bytes: bytes) -> str:
        """Infer image MIME type from magic bytes, not filename extension."""
        if image_bytes.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
            return "image/webp"
        return "image/jpeg"

    async def analyze_one(img_path: str, date: str) -> dict:
        with open(img_path, "rb") as f:
            image_bytes = f.read()
        img_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        media_type = detect_media_type(image_bytes)

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
                        "text": (
                            f"Wound photo timestamp: {date}. "
                            "Return the required wound assessment JSON only."
                        ),
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

    tasks = [analyze_one(p, d) for p, d in zip(image_paths, image_dates)]
    return await asyncio.gather(*tasks)


# ──────────────────────────────────────────────────────────────────────────
# AGENT 2 — TREND AGENT: Time-series wound trajectory
# ──────────────────────────────────────────────────────────────────────────

TREND_SYSTEM = """You are a wound progression analyst reviewing serial wound observations.
You are clinical decision support, not a diagnosis. Your output augments — does not replace — clinician judgment.

Given per-image wound assessments across multiple days, output STRICT JSON:
{
  "trajectory": "<improving|stable|deteriorating>",
  "size_change_pct": <float>,
  "granulation_change_pct": <float>,
  "infection_signal_change": "<resolving|stable|emerging|worsening>",
  "days_observed": <int>,
  "key_findings": ["<finding>", ...],
  "concerning_changes": ["<change>", ...]
}

Interpretation guidance:
- Negative size_change_pct means wound shrinking (generally favorable).
- Positive granulation_change_pct is generally favorable.
- Account for both wound-bed biology and periwound infection indicators.
- Return ONLY JSON."""


async def trend_agent(
    patient_id: str,
    wound_type: str,
    image_dates: list[str],
    vision_results: list[dict],
) -> dict:
    """Analyze wound trajectory across serial image assessments."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=TREND_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Patient ID: {patient_id}
Wound Type: {wound_type}
Observation Dates:
{json.dumps(image_dates, indent=2)}

Per-image wound vision outputs:
{json.dumps(vision_results, indent=2)}

Analyze trajectory and return the required JSON.""",
        }],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────
# AGENT 3 — RISK AGENT: Infection + complication risk
# ──────────────────────────────────────────────────────────────────────────

RISK_SYSTEM = """You are a clinical risk stratification analyst for chronic wound monitoring.
You are clinical decision support, not a diagnosis. Your output augments — does not replace — clinician judgment.

Given patient context, baseline wound metrics, and current visual findings, output STRICT JSON:
{
  "infection_risk_score": <float 0-1>,
  "infection_risk_level": "<low|moderate|high|critical>",
  "complication_likelihood": "<low|moderate|high>",
  "estimated_days_to_heal": <int or null>,
  "risk_factors": ["<factor>", ...],
  "protective_factors": ["<factor>", ...],
  "rationale": "<2-sentence clinical reasoning>"
}

Use conservative reasoning when uncertainty is high and mention uncertainty in rationale.
Return ONLY JSON."""


async def risk_agent(
    patient_id: str,
    wound_type: str,
    patient_context: dict,
    baseline_metrics: dict,
    vision_results: list[dict],
) -> dict:
    """Estimate infection and complication risk from context plus visual signals."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=RISK_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Patient ID: {patient_id}
Wound Type: {wound_type}
Patient Context:
{json.dumps(patient_context, indent=2)}

Baseline Metrics:
{json.dumps(baseline_metrics, indent=2)}

Latest Serial Visual Findings:
{json.dumps(vision_results, indent=2)}

Return the risk JSON.""",
        }],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────
# AGENT 4 — CARE AGENT: Synthesizes into daily care + escalation
# ──────────────────────────────────────────────────────────────────────────

CARE_SYSTEM = """You are a wound care coordination assistant for home-care and clinic follow-up.
You are clinical decision support, not a diagnosis. Your output augments — does not replace — clinician judgment.

Synthesize vision findings, trajectory analysis, and risk stratification into caregiver-safe guidance.

Output STRICT JSON:
{
  "escalation_level": "<CONTINUE_HOME_CARE|CALL_NURSE_24H|URGENT_CLINICIAN_SAME_DAY|ER_NOW>",
  "headline": "<one-line summary in caregiver-friendly language>",
  "today_actions": ["<action>", ...],
  "watch_for": ["<warning sign>", ...],
  "explanation": "<2-3 sentence plain-English explanation a non-medical person understands>",
  "clinical_summary": "<1-paragraph summary in clinical language for the nurse/doctor>",
  "confidence": "<LOW|MEDIUM|HIGH>",
  "citations": [
    {"signal": "vision|trend|risk", "claim": "<what the signal showed>"},
    ...
  ]
}

Return ONLY JSON."""


async def care_agent(
    patient_id: str,
    wound_type: str,
    patient_context: dict,
    vision_results: list[dict],
    trend_result: dict,
    risk_result: dict,
) -> dict:
    """Synthesize outputs into care guidance and escalation decision support."""

    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=CARE_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Patient ID: {patient_id}
Wound Type: {wound_type}
Patient Context:
{json.dumps(patient_context, indent=2)}

Vision Signal:
{json.dumps(vision_results, indent=2)}

Trend Signal:
{json.dumps(trend_result, indent=2)}

Risk Signal:
{json.dumps(risk_result, indent=2)}

Return care synthesis JSON.""",
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


async def run_pipeline(
    patient_id: str,
    wound_type: str,
    patient_context: dict,
    image_paths: list[str],
    image_dates: list[str],
    baseline_metrics: dict,
    progress_callback=None,
) -> dict:
    """Run the WOUND IQ pipeline with staged dependencies and progress streaming."""

    async def report(step: str, status: str, data=None):
        if progress_callback:
            await progress_callback({"step": step, "status": status, "data": data})

    if DEMO_MODE:
        # Bulletproof demo path: cached payloads + realistic staged latency.
        await report("vision", "running")
        await asyncio.sleep(6)
        vision_results = WOUND_PACKAGE["cached_vision"]
        await report("vision", "done", vision_results)

        await report("trend", "running")
        await report("risk", "running")
        await asyncio.sleep(8)
        trend_result = WOUND_PACKAGE["cached_trend"]
        risk_result = WOUND_PACKAGE["cached_risk"]
        await report("trend", "done", trend_result)
        await asyncio.sleep(0.4)
        await report("risk", "done", risk_result)

        await report("care", "running")
        await asyncio.sleep(6)
        care = WOUND_PACKAGE["cached_care"]
        await report("care", "done", care)

        return {
            "patient_id": patient_id,
            "wound_type": wound_type,
            "patient_context": patient_context,
            "vision": vision_results,
            "trend": trend_result,
            "risk": risk_result,
            "care": care,
        }

    # Stage 1: Vision over all images (parallel per-image within agent)
    await report("vision", "running")
    vision_results = await wound_vision_agent(image_paths, image_dates)
    await report("vision", "done", vision_results)

    # Stage 2: Trend + risk in parallel (both depend on vision)
    await report("trend", "running")
    await report("risk", "running")

    trend_task = trend_agent(patient_id, wound_type, image_dates, vision_results)
    risk_task = risk_agent(
        patient_id,
        wound_type,
        patient_context,
        baseline_metrics,
        vision_results,
    )

    trend_result, risk_result = await asyncio.gather(trend_task, risk_task)

    await report("trend", "done", trend_result)
    await report("risk", "done", risk_result)

    # Stage 3: Care synthesis
    await report("care", "running")
    care = await care_agent(
        patient_id,
        wound_type,
        patient_context,
        vision_results,
        trend_result,
        risk_result,
    )
    await report("care", "done", care)

    return {
        "patient_id": patient_id,
        "wound_type": wound_type,
        "patient_context": patient_context,
        "vision": vision_results,
        "trend": trend_result,
        "risk": risk_result,
        "care": care,
    }
