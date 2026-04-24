"""Demo data package for WOUND IQ clinical decision support demo."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "images"
DEMO_MODE = True

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
    "cached_vision": [
        {
            "date": "Day 1 (initial assessment)",
            "image_path": str(DATA_DIR / "ankle_day01.png"),
            "estimated_dimensions_mm": {
                "length": 38,
                "width": 22,
                "depth_estimate": "partial-thickness",
            },
            "tissue_composition_pct": {
                "granulation": 35,
                "slough": 50,
                "eschar": 10,
                "epithelial": 5,
            },
            "wound_bed_color": "mixed",
            "exudate": {"amount": "moderate", "type": "serous"},
            "periwound_skin": {
                "erythema_present": True,
                "edema_present": True,
                "maceration_present": False,
                "redness_extent_mm": 8,
            },
            "infection_indicators": ["mild periwound erythema"],
            "image_quality": "good",
            "confidence": 0.88,
            "notes": "Established diabetic foot ulcer, mixed tissue, mild surrounding inflammation.",
        },
        {
            "date": "Day 7",
            "image_path": str(DATA_DIR / "ankle_day03.png"),
            "estimated_dimensions_mm": {
                "length": 34,
                "width": 20,
                "depth_estimate": "partial-thickness",
            },
            "tissue_composition_pct": {
                "granulation": 55,
                "slough": 30,
                "eschar": 5,
                "epithelial": 10,
            },
            "wound_bed_color": "red",
            "exudate": {"amount": "minimal", "type": "serous"},
            "periwound_skin": {
                "erythema_present": True,
                "edema_present": False,
                "maceration_present": False,
                "redness_extent_mm": 5,
            },
            "infection_indicators": [],
            "image_quality": "good",
            "confidence": 0.91,
            "notes": "Improving - granulation up, exudate down, erythema receding.",
        },
        {
            "date": "Day 14 (mid-treatment)",
            "image_path": str(DATA_DIR / "ankle_day07.png"),
            "estimated_dimensions_mm": {
                "length": 32,
                "width": 21,
                "depth_estimate": "partial-thickness",
            },
            "tissue_composition_pct": {
                "granulation": 40,
                "slough": 45,
                "eschar": 5,
                "epithelial": 10,
            },
            "wound_bed_color": "yellow",
            "exudate": {"amount": "moderate", "type": "purulent"},
            "periwound_skin": {
                "erythema_present": True,
                "edema_present": True,
                "maceration_present": True,
                "redness_extent_mm": 14,
            },
            "infection_indicators": [
                "expanding erythema halo",
                "purulent exudate",
                "edema returning",
            ],
            "image_quality": "good",
            "confidence": 0.89,
            "notes": "CONCERNING - trajectory reversed, erythema halo expanded 5mm to 14mm, exudate now purulent.",
        },
        {
            "date": "Day 21 (current)",
            "image_path": str(DATA_DIR / "ankle_day14.png"),
            "estimated_dimensions_mm": {
                "length": 35,
                "width": 24,
                "depth_estimate": "full-thickness",
            },
            "tissue_composition_pct": {
                "granulation": 20,
                "slough": 60,
                "eschar": 15,
                "epithelial": 5,
            },
            "wound_bed_color": "yellow",
            "exudate": {"amount": "heavy", "type": "purulent"},
            "periwound_skin": {
                "erythema_present": True,
                "edema_present": True,
                "maceration_present": True,
                "redness_extent_mm": 22,
            },
            "infection_indicators": [
                "heavy purulent exudate",
                "erythema >2cm from margin",
                "wound enlarging",
                "full-thickness progression",
            ],
            "image_quality": "good",
            "confidence": 0.93,
            "notes": "ACTIVE INFECTION - meets multiple CDC infection criteria.",
        },
    ],
    "cached_trend": {
        "trajectory": "deteriorating",
        "size_change_pct": -7.9,
        "granulation_change_pct": -42.9,
        "infection_signal_change": "worsening",
        "days_observed": 21,
        "key_findings": [
            "Initial improvement Day 1 to 7 (granulation 35% to 55%)",
            "Trajectory reversed at Day 14 - granulation dropped, slough increased",
            "Day 21 shows clear deterioration with heavy purulent exudate",
            "Periwound erythema progressed 8mm to 22mm",
        ],
        "concerning_changes": [
            "Erythema halo exceeds 2cm - meets CDC infection criterion",
            "Wound depth progressed partial to full-thickness",
            "Granulation tissue lost 43% from peak",
            "Exudate transitioned serous to purulent at Day 14",
        ],
    },
    "cached_risk": {
        "infection_risk_score": 0.87,
        "infection_risk_level": "high",
        "complication_likelihood": "high",
        "estimated_days_to_heal": None,
        "risk_factors": [
            "Multiple CDC infection criteria met (purulent drainage, erythema >2cm, edema)",
            "HbA1c 8.4% - poor glycemic control impairs healing",
            "Peripheral neuropathy + PAD reduce healing capacity",
            "Wound progressed to full-thickness (Wagner Grade 2 to 3 trajectory)",
        ],
        "protective_factors": [
            "Adequate perfusion (ABI 0.78) supports healing if infection controlled",
            "No prior amputations",
            "Active medical engagement",
        ],
        "rationale": "Multiple CDC infection surveillance criteria are now met. Trajectory reversal at Day 14 with progression to full-thickness signals active infection requiring urgent clinician evaluation.",
    },
    "cached_care": {
        "escalation_level": "URGENT_CLINICIAN_SAME_DAY",
        "headline": "Active infection signs detected - patient needs same-day clinical evaluation.",
        "today_actions": [
            "Contact wound care clinic or PCP today for same-day visit",
            "Do not weight-bear on the affected foot - strict offloading",
            "Take wound photos before and after dressing change for clinician review",
            "Bring current medication list (including aspirin) to the appointment",
            "Document temperature 2x today; report fever >100.4F immediately",
        ],
        "watch_for": [
            "Fever, chills, or feeling unwell - call 911 or go to ER",
            "Red streaking up the leg - emergency",
            "Spreading redness beyond current 22mm halo",
            "New or worsening foot pain (despite neuropathy)",
            "Increased drainage, foul odor, or color change",
        ],
        "explanation": "The wound was healing well through Day 7, but reversed direction by Day 14 and now shows clear signs of infection - the surrounding redness has spread, the drainage has turned cloudy, and the wound has gotten deeper. This pattern needs a clinician's eyes today. With prompt antibiotic treatment, this is highly manageable. Without it, infections in diabetic foot wounds can progress quickly.",
        "clinical_summary": "62yo M with T2DM (HbA1c 8.4), peripheral neuropathy, and PAD presenting with deteriorating right plantar diabetic foot ulcer. Serial imaging Days 1-21 demonstrates initial improvement followed by trajectory reversal at Day 14: granulation decreased from peak 55% to 20%, exudate converted serous-to-purulent, periwound erythema expanded from 5mm to 22mm (>2cm threshold), and wound deepened from partial- to full-thickness. Multiple CDC SSI surveillance criteria are met. Recommend same-day clinical evaluation with consideration for empiric oral antibiotic coverage pending wound culture, vascular assessment, and possible imaging to rule out underlying osteomyelitis.",
        "confidence": "HIGH",
        "citations": [
            {
                "signal": "vision",
                "claim": "Periwound erythema expanded from 8mm (Day 1) to 22mm (Day 21), exceeding 2cm CDC threshold.",
            },
            {
                "signal": "vision",
                "claim": "Exudate transitioned from serous to purulent between Day 7 and Day 14.",
            },
            {
                "signal": "trend",
                "claim": "Granulation tissue decreased 43% from peak; trajectory shifted from improving to deteriorating.",
            },
            {
                "signal": "risk",
                "claim": "Infection risk score 0.87 (high) with multiple CDC criteria met and HbA1c 8.4 impairing healing.",
            },
        ],
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
