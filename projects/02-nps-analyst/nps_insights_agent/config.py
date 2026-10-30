"""Configuration, NPS Rules, House Assumptions, Verdicts & Model Setup.

Centralizes all rules required by the NPS Analyst in a Box project brief:
1. Score Buckets: Promoters (9-10), Passives (7-8), Detractors (0-6).
2. Low-Sample Guardrail: Segments with <30 responses are marked `low_sample=True`.
3. Churn Rate Assumptions: Promoter 3%, Passive 10%, Detractor 25%.
4. Verdict Lookup Tables: Health verdicts, Risk verdicts, and Executive Alert levels.
5. Model Configuration: AWS Strands BedrockModel (Nova Lite) with OpenAI fallback.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# =============================================================================
# 1. File Paths & Survey Schema
# =============================================================================

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
DEFAULT_SURVEY_PATH = Path(
    os.getenv("NPS_SURVEY_PATH", str(PROJECT_ROOT / "data" / "nps_survey.csv"))
)

REQUIRED_COLUMNS = (
    "response_id",
    "date",
    "month",
    "product",
    "tenure",
    "channel",
    "score",
    "comment",
    "annual_revenue_inr",
)

SEGMENT_COLUMNS = ("month", "product", "channel", "tenure")

# =============================================================================
# 2. NPS Statistical & House Rules
# =============================================================================

PROMOTER_MIN_SCORE = 9
PASSIVE_MIN_SCORE = 7
DETRACTOR_MAX_SCORE = 6

# Any segment with fewer than 30 answers has a wide margin of error and must
# be flagged `low_sample = True` so agents never crown it best or worst.
MIN_SAMPLE_SIZE = 30

# =============================================================================
# 3. Finance Assumptions: Annual Churn Probability by Bucket
# =============================================================================

CHURN_RATES: dict[str, float] = {
    "promoter": 0.03,   # 3% annual churn assumption
    "passive": 0.10,    # 10% annual churn assumption
    "detractor": 0.25,  # 25% annual churn assumption
}

LAKH_INR = 100_000.0  # 1 lakh = ₹1,00,000

# =============================================================================
# 4. Deterministic Verdict Lookup Tables ("Verdicts come from tables, not moods")
# =============================================================================


def get_nps_health_verdict(nps: float) -> str:
    """Deterministic table mapping an NPS score (-100 to +100) to a health verdict."""
    if nps >= 50.0:
        return "EXCELLENT"
    if nps >= 30.0:
        return "GOOD"
    if nps >= 0.0:
        return "NEEDS WORK"
    return "CRITICAL"


def get_revenue_risk_verdict(revenue_at_risk_lakh: float, total_revenue_lakh: float) -> str:
    """Deterministic table mapping expected revenue at risk to a financial risk verdict."""
    risk_share_pct = (
        (revenue_at_risk_lakh / total_revenue_lakh * 100.0) if total_revenue_lakh > 0 else 0.0
    )
    if revenue_at_risk_lakh >= 30.0 or risk_share_pct >= 10.0:
        return "HIGH"
    if revenue_at_risk_lakh >= 15.0 or risk_share_pct >= 5.0:
        return "MODERATE"
    return "LOW"


def get_alert_level(
    overall_nps: float,
    latest_month_nps: float,
    nps_drop_pts: float,
    revenue_at_risk_lakh: float,
) -> str:
    """Deterministic table for the CEO Brief Alert Level (RED / AMBER / GREEN).

    Rules:
    - RED   : Latest month NPS < 0 (negative territory), OR overall NPS < 0,
              OR monthly drop >= 20 points, OR revenue at risk >= ₹30 lakh.
    - AMBER : Overall NPS < 30 ("NEEDS WORK"), OR monthly drop >= 10 points,
              OR revenue at risk >= ₹15 lakh.
    - GREEN : Overall NPS >= 30, latest month >= 20, drop < 10 points, and risk < ₹15 lakh.
    """
    if (
        latest_month_nps < 0.0
        or overall_nps < 0.0
        or nps_drop_pts >= 20.0
        or revenue_at_risk_lakh >= 30.0
    ):
        return "RED"
    if overall_nps < 30.0 or nps_drop_pts >= 10.0 or revenue_at_risk_lakh >= 15.0:
        return "AMBER"
    return "GREEN"


# =============================================================================
# 5. Comment Theme Taxonomy & Keyword Rules
# =============================================================================

THEME_DEFINITIONS: dict[str, dict[str, object]] = {
    "otp_login": {
        "label": "OTP & Login Failure After App Update",
        "description": "Delayed/missing OTP verification codes, account lockouts, and login failures following the mobile app update.",
        "keywords": [
            "otp",
            "verification code",
            "asking for a code",
            "login",
            "logging me out",
            "locked out",
            "get into my account",
            "after the update",
        ],
    },
    "fees_and_charges": {
        "label": "Wealth Advisory Fees & Account/Card Charges",
        "description": "High/unexplained quarterly wealth advisory fees, hidden portfolio costs, credit card annual fees, and minimum balance penalties.",
        "keywords": [
            "fee",
            "fees",
            "charges",
            "hidden costs",
            "paying so much",
            "penalty",
            "minimum balance",
            "late payment",
        ],
    },
    "app_performance": {
        "label": "App Crashes, Glitches & Slowness",
        "description": "Mobile app crashes on statements page, payment hangs, freezes, and peak-hour slowness.",
        "keywords": [
            "app crashes",
            "app is slow",
            "glitches in the app",
            "freezes sometimes",
            "slow during peak hours",
            "hangs while making",
        ],
    },
    "call_centre_ivr": {
        "label": "Call Centre Wait Times, Hold Drops & IVR Loops",
        "description": "Endless IVR menus, 40-minute hold times, dropped calls, and late callbacks.",
        "keywords": [
            "ivr",
            "on hold",
            "call centre",
            "waiting time is long",
            "wait a long time",
            "callback was promised",
            "call dropped",
        ],
    },
    "interest_rates_rewards": {
        "label": "FD/Savings Interest Rates & Card Reward Expiry",
        "description": "Lower savings/FD interest rates compared to competitors and expiring credit card reward points.",
        "keywords": [
            "interest rate",
            "interest rates",
            "fd rates",
            "moving my fd",
            "earns more at other banks",
            "reward points expire",
        ],
    },
    "positive_mismatch": {
        "label": "Score-Comment Mismatch (Glowing Praise on Low Score)",
        "description": "Customers who gave a 0 or 1 detractor score while writing enthusiastic praise (likely inverted scale confusion).",
        "keywords": [
            "amazing support",
            "excellent service",
            "best bank i have used",
            "love the app",
            "very happy with my bank",
        ],
    },
    "fast_digital_payments": {
        "label": "Fast UPI, Bill Pay & Smooth Digital Onboarding",
        "description": "Quick UPI/recharge payments, smooth online account opening, and reliable transfers.",
        "keywords": [
            "upi payments",
            "mobile recharge",
            "opening the account was smooth",
            "transfers are fast",
            "seamless experience",
        ],
    },
    "branch_and_rm_service": {
        "label": "Helpful Branch Staff & Relationship Managers",
        "description": "Fast branch KYC updates, patient branch staff, and responsive relationship managers.",
        "keywords": [
            "branch team sorted",
            "branch staff are helpful",
            "my rm explained",
            "relationship manager is very helpful",
        ],
    },
    "card_cashback_rewards": {
        "label": "Credit Card Cashback & Useful Rewards",
        "description": "Strong monthly credit card cashback and useful reward redemptions.",
        "keywords": [
            "great cashback",
            "reward points on my card are actually useful",
        ],
    },
    "general_sentiment": {
        "label": "General Service Sentiment (Non-Specific)",
        "description": "Broad positive, neutral, or negative remarks without a specific operational root cause.",
        "keywords": [
            "not happy with the service lately",
            "average experience",
            "does the job",
            "nothing special",
            "good bank, no complaints",
            "happy with the overall service",
        ],
    },
}

# Positive/negative phrases for detecting score-comment mismatches
POSITIVE_PRAISE_PATTERNS = (
    "amazing support",
    "excellent service",
    "best bank",
    "love the app",
    "very happy",
    "thank you",
)

NEGATIVE_COMPLAINT_PATTERNS = (
    "broken",
    "never arrives",
    "locked out",
    "hidden costs",
    "not happy",
    "frustrating",
)


# =============================================================================
# 6. Model Factory (AWS Strands + Bedrock Nova Lite / OpenAI)
# =============================================================================


def get_model():
    """Return a configured Strands Model instance.

    Defaults to Amazon Bedrock (`amazon.nova-lite-v1:0`) matching Project 01,
    and supports OpenAI (`NPS_PROVIDER=openai` or `OPENAI_MODEL`) when requested.
    """
    provider = os.getenv("NPS_PROVIDER", "bedrock").strip().lower()
    if provider == "openai":
        from strands.models.openai import OpenAIModel

        model_id = os.getenv("NPS_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        return OpenAIModel(model_id=model_id)

    from strands.models.bedrock import BedrockModel

    model_id = os.getenv("NPS_MODEL", os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"))
    region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    os.environ.setdefault("AWS_REGION", region)
    return BedrockModel(
        model_id=model_id,
        region_name=region,
        max_tokens=4096,
        temperature=0.0,
    )


def get_model_description() -> str:
    """Human-readable label of the active LLM provider and model."""
    provider = os.getenv("NPS_PROVIDER", "bedrock").strip().lower()
    if provider == "openai":
        model_id = os.getenv("NPS_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        return f"OpenAI ({model_id})"
    model_id = os.getenv("NPS_MODEL", os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"))
    region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    return f"Amazon Bedrock ({model_id} in {region})"

