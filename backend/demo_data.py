"""
Demo data package. For the hackathon demo, we pre-stage:
  - 4 parking lot images (you'll drop these in /data/images/)
  - Realistic Google Trends numbers for the ticker's brand
  - Analyst consensus + fundamentals
  - The actual earnings outcome (for the mic-drop reveal)

For COST, we're staging a Q3 2024 setup where parking traffic + search
trends both accelerated but Wall Street was still modeling conservatively.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "images"

# ──────────────────────────────────────────────────────────────────────────
# COSTCO — Q3 FY2024 setup
# ──────────────────────────────────────────────────────────────────────────

COST_PACKAGE = {
    "ticker": "COST",
    "brand": "Costco",

    # 4 parking lot images across a quarter (pre-earnings)
    # User drops these into /data/images/ before the demo
    "image_paths": [
        str(DATA_DIR / "cost_week01.jpg"),
        str(DATA_DIR / "cost_week05.jpg"),
        str(DATA_DIR / "cost_week09.jpg"),
        str(DATA_DIR / "cost_week12.jpg"),
    ],
    "image_dates": [
        "2024-06-15 (early quarter)",
        "2024-07-20 (mid quarter)",
        "2024-08-17 (late quarter)",
        "2024-09-07 (just before earnings)",
    ],

    # Realistic Google Trends weekly interest scores for "Costco"
    # Shows acceleration through the quarter
    "trends_data": {
        "search_term": "Costco",
        "geography": "US",
        "weekly_interest_2024": {
            "2024-06-09": 72, "2024-06-16": 74, "2024-06-23": 71, "2024-06-30": 78,
            "2024-07-07": 80, "2024-07-14": 79, "2024-07-21": 82, "2024-07-28": 85,
            "2024-08-04": 84, "2024-08-11": 87, "2024-08-18": 89, "2024-08-25": 88,
            "2024-09-01": 91, "2024-09-08": 93,
        },
        "weekly_interest_2023_same_period": {
            "2023-06-11": 68, "2023-06-18": 70, "2023-06-25": 69, "2023-07-02": 71,
            "2023-07-09": 72, "2023-07-16": 73, "2023-07-23": 72, "2023-07-30": 75,
            "2023-08-06": 74, "2023-08-13": 76, "2023-08-20": 77, "2023-08-27": 76,
            "2023-09-03": 78, "2023-09-10": 79,
        },
        "related_rising_queries": [
            "costco membership cost",
            "costco hours near me",
            "costco kirkland",
            "is costco worth it",
        ],
    },

    # Fundamentals + street expectations going into Sept 26, 2024 earnings
    "fundamentals": {
        "earnings_date": "2024-09-26",
        "quarter_reporting": "Q4 FY2024",
        "consensus_estimates": {
            "same_store_sales_growth_pct_ex_gas_fx": 6.5,
            "eps": 5.08,
            "revenue_billions": 79.8,
        },
        "price_90d_ago": 845.32,
        "price_current": 893.15,
        "price_performance_90d_pct": 5.66,
        "implied_earnings_move_from_options": 4.2,
        "analyst_notes": [
            "JPM: traffic strong but membership renewal already priced in",
            "BofA: valuation stretched at 52x forward P/E",
            "MS: overweight, but acknowledges limited upside vs modest setup",
            "GS: concerned about deceleration in discretionary categories",
        ],
        "recent_monthly_sales_reports": {
            "June 2024 SSS ex-gas/fx": "+6.9%",
            "July 2024 SSS ex-gas/fx": "+7.2%",
            "August 2024 SSS ex-gas/fx": "+7.1%",
        },
    },

    # The ACTUAL result (for the reveal after the demo)
    # Sept 26, 2024 — COST reported +6.9% SSS ex-gas/fx, beat EPS
    # Stock actually traded down slightly on the print due to valuation,
    # but the traffic/trends signal was correct directionally.
    "actual_outcome": {
        "reported_ss_sales_growth_pct": 6.9,
        "reported_eps": 5.29,
        "beat_consensus_sss": True,
        "beat_consensus_eps": True,
        "stock_reaction_pct": -1.4,
        "note": (
            "COST beat both SSS (+6.9% vs +6.5% consensus) and EPS "
            "($5.29 vs $5.08 consensus). Traffic signals correctly flagged "
            "acceleration. Stock sold off modestly on valuation despite the "
            "beat — a reminder that alpha-data signals predict fundamentals, "
            "not always short-term price. The 90-day forward return was "
            "+8.2% as the market eventually repriced."
        ),
    },
}


PACKAGES = {
    "COST": COST_PACKAGE,
}


def get_demo_package(ticker: str) -> dict:
    """Return the demo package for a ticker. Defaults to COST."""
    return PACKAGES.get(ticker.upper(), COST_PACKAGE)
