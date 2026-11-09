"""
Shared verdict/confidence logic so URL, message, and file scans always
report risk consistently across the whole platform.
"""

SAFE_MAX = 30
SUSPICIOUS_MAX = 65


def to_verdict(risk_score: float) -> str:
    if risk_score < SAFE_MAX:
        return "safe"
    if risk_score < SUSPICIOUS_MAX:
        return "suspicious"
    return "malicious"


def confidence_for(risk_score: float) -> float:
    """
    Confidence is highest when the score is far from a threshold boundary,
    and lowest right at the boundary (genuinely ambiguous cases).
    Returns a percentage 0-100.
    """
    boundaries = [0, SAFE_MAX, SUSPICIOUS_MAX, 100]
    nearest_gap = min(abs(risk_score - b) for b in boundaries)
    # widen out to a 0-100 confidence scale, capping at 97 (never claim certainty)
    confidence = 55 + min(nearest_gap * 2.2, 42)
    return round(min(confidence, 97), 1)


def build_result(scan_type: str, target: str, engine_output: dict) -> dict:
    risk_score = engine_output["risk_score"]
    return {
        "scan_type": scan_type,
        "target": target,
        "verdict": to_verdict(risk_score),
        "risk_score": risk_score,
        "confidence": confidence_for(risk_score),
        "explanation": engine_output["explanation"],
        "factors": engine_output.get("factors", []),
        "details": engine_output.get("details"),
    }
