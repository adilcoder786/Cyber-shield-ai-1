"""
Phishing email/message/SMS analyzer.
Combines rule-based NLP heuristics (urgency, sensitive-data requests, generic
greetings, spoof patterns) with a TF-IDF + Logistic Regression text
classifier, and cross-checks any embedded URLs with the URL analyzer.
"""
import re
from pathlib import Path
import joblib

from app.engine.url_analyzer import analyze_url

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "message_model.joblib"
_model_cache = None

URL_REGEX = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+|\b[a-z0-9.-]+\.(?:com|net|org|tk|ml|xyz|top|click|info)\b[^\s<>\"']*)", re.IGNORECASE)

URGENCY_PHRASES = [
    "act now", "immediately", "urgent", "within 24 hours", "verify now",
    "act fast", "limited time", "expires today", "final notice", "asap",
    "before it's too late", "final reminder", "account will be closed",
    "account will be suspended", "avoid suspension", "risk of closure",
]

SENSITIVE_DATA_REQUESTS = [
    "password", "otp", "one-time password", "cvv", "card number",
    "social security", "ssn", "pin", "bank account", "routing number",
    "seed phrase", "login credentials", "date of birth", "security code",
]

MONEY_BAIT_PHRASES = [
    "you have won", "congratulations", "claim your prize", "free gift",
    "gift card", "lottery", "wire transfer", "processing fee", "refund of",
    "cash reward", "you've been selected",
]

GENERIC_GREETINGS = ["dear customer", "dear user", "dear valued customer", "dear account holder", "dear sir/madam"]

THREAT_PHRASES = [
    "account has been suspended", "account will be locked", "unusual activity",
    "suspicious activity", "legal action", "your account is limited",
    "failure to respond", "permanently closed", "permanently revoked",
]


def _load_model():
    global _model_cache
    if _model_cache is None and MODEL_PATH.exists():
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def _find_phrases(text_lower: str, phrase_list):
    return [p for p in phrase_list if p in text_lower]


def _rule_based_score(content: str):
    text_lower = content.lower()
    reasons = []
    score = 0

    urgency_hits = _find_phrases(text_lower, URGENCY_PHRASES)
    if urgency_hits:
        w = min(8 * len(urgency_hits), 24)
        score += w
        reasons.append((f"Uses urgency/pressure language ({urgency_hits[0]})", w))

    sensitive_hits = _find_phrases(text_lower, SENSITIVE_DATA_REQUESTS)
    if sensitive_hits:
        w = min(12 * len(sensitive_hits), 30)
        score += w
        reasons.append((f"Requests sensitive information ({', '.join(sensitive_hits[:3])})", w))

    money_hits = _find_phrases(text_lower, MONEY_BAIT_PHRASES)
    if money_hits:
        w = min(10 * len(money_hits), 24)
        score += w
        reasons.append((f"Contains reward/prize bait language ({money_hits[0]})", w))

    greeting_hits = _find_phrases(text_lower, GENERIC_GREETINGS)
    if greeting_hits:
        score += 10
        reasons.append(("Uses a generic greeting instead of your actual name", 10))

    threat_hits = _find_phrases(text_lower, THREAT_PHRASES)
    if threat_hits:
        w = min(10 * len(threat_hits), 20)
        score += w
        reasons.append((f"Threatens negative consequences ({threat_hits[0]})", w))

    caps_words = re.findall(r"\b[A-Z]{4,}\b", content)
    if len(caps_words) >= 2:
        score += 6
        reasons.append(("Excessive use of ALL CAPS for emphasis", 6))

    exclamations = content.count("!")
    if exclamations >= 3:
        score += 6
        reasons.append(("Excessive exclamation marks, common in scam messaging", 6))

    return min(score, 100), reasons


def analyze_message(content: str, channel: str = "email", sender: str = None) -> dict:
    rule_score, rule_reasons = _rule_based_score(content)

    ml_probability = None
    bundle = _load_model()
    if bundle:
        vec = bundle["vectorizer"].transform([content])
        proba = bundle["model"].predict_proba(vec)[0]
        ml_probability = float(proba[1]) * 100

    # Cross-check embedded links
    found_urls = list(dict.fromkeys(URL_REGEX.findall(content)))[:5]
    url_analyses = []
    max_url_risk = 0
    for u in found_urls:
        result = analyze_url(u)
        url_analyses.append({"url": u, "risk_score": result["risk_score"], "explanation": result["explanation"][:3]})
        max_url_risk = max(max_url_risk, result["risk_score"])

    if ml_probability is not None:
        combined = 0.5 * rule_score + 0.35 * ml_probability + 0.15 * max_url_risk
    else:
        combined = 0.75 * rule_score + 0.25 * max_url_risk

    combined = round(min(combined, 100), 1)

    if found_urls and max_url_risk >= 60:
        rule_reasons.append((f"Contains a high-risk link ({found_urls[0][:50]})", 20))

    # Sender/display-name spoof heuristic
    if sender:
        free_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        looks_official = any(b in content.lower() for b in ["bank", "paypal", "microsoft", "apple", "amazon", "netflix"])
        if looks_official and any(sender.lower().endswith("@" + d) for d in free_domains):
            rule_reasons.append(("Claims to be an official organization but sent from a free personal email domain", 18))
            combined = min(100, combined + 10)

    explanation = [r for r, _ in sorted(rule_reasons, key=lambda x: -x[1])]
    if not explanation:
        explanation = ["No known phishing language patterns detected in this message."]

    factors = [{"label": r, "weight": w, "category": "content"} for r, w in rule_reasons]

    return {
        "risk_score": combined,
        "rule_score": rule_score,
        "ml_probability": ml_probability,
        "explanation": explanation,
        "factors": factors,
        "details": {
            "channel": channel,
            "sender": sender,
            "urls_found": url_analyses,
        },
    }
