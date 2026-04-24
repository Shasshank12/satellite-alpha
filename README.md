# WOUND IQ

Multi-agent clinical decision support for chronic wound monitoring.

Disclaimer: Decision support, not diagnosis. Outputs augment and do not replace clinician judgment.

## What It Does

WOUND IQ analyzes serial wound photos and generates caregiver-safe escalation guidance.

Inputs:

- 4 wound images over time
- Patient context
- Baseline wound metrics

Pipeline:

- Vision Analyst: extracts dimensions, tissue mix, exudate, periwound flags, infection indicators
- Trend Tracker: computes trajectory and signal change across days
- Risk Engine: estimates infection/complication risk from context plus visual findings
- Care Coordinator: synthesizes signals into today actions, watch-fors, and escalation level

Output:

- Escalation level: CONTINUE_HOME_CARE, CALL_NURSE_24H, URGENT_CLINICIAN_SAME_DAY, or ER_NOW
- Plain-English instructions for caregiver + clinical summary for nurse/doctor

## Quick Start

1. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Create .env in project root:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

3. Add demo wound images to data/images:

- wound_day01.jpg
- wound_day07.jpg
- wound_day14.jpg
- wound_day21.jpg

4. Run app:

```bash
cd ..
./run.sh
```

5. Open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000

## Architecture

All agents run on claude-opus-4-7.

Dependency graph:

1. Stage 1: Vision runs first, with all images processed in parallel inside the agent
2. Stage 2: Trend + Risk run in parallel after vision completes
3. Stage 3: Care agent synthesizes all prior outputs

Server streaming:

- FastAPI /analyze returns Server-Sent Events (SSE)
- Frontend updates each agent card in real time
- /reveal/{patient_id} provides the mic-drop actual outcome

## Demo Script

"Diabetic foot ulcers progress to amputation in 14 to 24 percent of cases when infection is caught too late. Wound care nurses are scarce in rural areas. Patients monitor wounds at home with no clinical eyes between appointments.

WOUND IQ uses four Claude agents to give caregivers and underserved clinics a clinical-grade second opinion from a phone photo.

Here's a real diabetic foot ulcer over 21 days. [RUN]

The Vision Analyst measures dimensions and tissue composition across 4 photos. The Trend Tracker computes the healing trajectory — size shrinking 12%, but granulation tissue dropping. The Risk Engine flags an emerging infection signal on Day 14. The Care Coordinator escalates: URGENT CLINICIAN SAME DAY.

[REVEAL]

This patient developed cellulitis on Day 19, requiring IV antibiotics and a 6-day hospital admission. If our system had been running, the Day 14 escalation would have caught it 5 days earlier — oral antibiotics, no admission, $14,000 saved, amputation risk lowered.

Built in 2 hours with Claude Opus 4.7. Decision support, not diagnosis."

## Demo Data

Default case ID: DEMO-001

Case profile:

- 62-year-old with type 2 diabetes, HbA1c 8.4
- Diabetic foot ulcer, plantar surface, right foot
- Peripheral neuropathy + hypertension

Reveal outcome:

- Cellulitis on Day 19, IV antibiotics required
- Counterfactual with earlier action: fewer hospital days, lower cost, reduced amputation risk

## Notes

- This app is for hackathon demonstration and educational decision support.
- Do not represent outputs as a medical diagnosis.
