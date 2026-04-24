"""Demo data package for WOUND IQ clinical decision support demo."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "images"

# ──────────────────────────────────────────────────────────────────────────
# WOUND IQ — DEMO CASE
# ──────────────────────────────────────────────────────────────────────────

WOUND_PACKAGE = {
    "patient_id": "DEMO-001",
    "wound_type": "Diabetic foot ulcer, plantar surface, right foot",
    "patient_context": {
        "age": 62,
        "diabetes_type": 2,
        "hba1c": 8.4,
        "comorbidities": ["peripheral neuropathy", "hypertension"],
        "weeks_since_onset": 3,
        "disclaimer": (
            "Decision support, not diagnosis. Outputs flag concerning visual "
            "indicators for clinician review."
        ),
    },
    "image_paths": [
        str(DATA_DIR / "ankle_day01.png"),
        str(DATA_DIR / "ankle_day03.png"),
        str(DATA_DIR / "ankle_day07.png"),
        str(DATA_DIR / "ankle_day14.png"),
    ],
    "image_dates": [
        "Day 1 (initial assessment)",
        "Day 3",
        "Day 7 (mid-treatment)",
        "Day 14 (current)",
    ],
    "baseline_metrics": {
        "initial_wound_size_mm": {"length": 38, "width": 22},
        "notes": "Decision support baseline only; not a definitive diagnosis.",
    },
    "actual_outcome": {
        "what_happened": (
            "Patient developed cellulitis on Day 19, required IV antibiotics. "
            "Caught earlier (Day 14) by clinician review, IV admission could "
            "have been prevented with oral antibiotics started on Day 15."
        ),
        "outcome_with_early_intervention": (
            "Estimated 6 fewer hospital days, $14,200 in avoided costs, "
            "reduced amputation risk"
        ),
        "statistical_context": (
            "Diabetic foot ulcers progress to amputation in 14-24% of cases "
            "when infection is missed. Early detection reduces this by ~70%."
        ),
        "days_earlier_flagged": 5,
        "disclaimer": (
            "Educational demo only. Decision support, not diagnosis. Clinical "
            "decisions require licensed clinician evaluation."
        ),
    },
}


PACKAGES = {
    "DEMO-001": WOUND_PACKAGE,
}


def get_demo_package(patient_id: str) -> dict:
    """Return the demo package for a patient id. Defaults to DEMO-001."""
    return PACKAGES.get(patient_id.upper(), WOUND_PACKAGE)
