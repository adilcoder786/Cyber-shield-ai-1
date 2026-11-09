"""
URL / website risk analyzer.
Combines transparent rule-based heuristics (for explainability) with a
scikit-learn RandomForest model (for pattern generalization) and, when
available, live threat-intelligence lookups.
"""
from pathlib import Path
import joblib

from app.ml.url_features import extract_url_features, FEATURE_ORDER
from app.engine import threat_intel

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "url_model.joblib"

_model_cache = None


def _load_model():
    global _model_cache
    if _model_cache is None and MODEL_PATH.exists():
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def _rule_based_score(features: dict, meta: dict):
    """Returns (score_0_100, [ (reason, weight) ]) purely from transparent rules."""
    reasons = []
    score = 0

    if features["is_ip_host"]:
        score += 22
        reasons.append(("Website address uses a raw IP instead of a domain name", 22))
    if features["has_at_symbol"]:
        score += 18
        reasons.append(("URL contains an '@' symbol, a classic redirect-masking trick", 18))
    if not features["has_https"]:
        score += 8
        reasons.append(("Connection is not secured with HTTPS", 8))
    if features["is_shortener"]:
        score += 12
        reasons.append(("URL uses a link-shortening service, hiding the real destination", 12))
    if features["is_punycode"]:
        score += 20
        reasons.append(("Domain uses punycode encoding, often used for lookalike characters", 20))
    if features["suspicious_tld"]:
        score += 14
        reasons.append((f"Domain uses a high-risk top-level domain (.{meta['tld']})", 14))
    if features["brand_impersonation"]:
        brands = ", ".join(meta["brand_in_domain"])
        score += 26
        reasons.append((f"Domain references a known brand ({brands}) but is not that brand's real site", 26))
    if features["num_subdomains"] >= 3:
        score += 10
        reasons.append(("Unusually deep subdomain nesting, often used to disguise the real host", 10))
    if features["num_hyphens"] >= 2:
        score += 8
        reasons.append(("Domain contains multiple hyphens, a common phishing pattern", 8))
    if features["num_suspicious_words"] >= 2:
        words = ", ".join(meta["suspicious_words_found"][:4])
        score += 12
        reasons.append((f"URL contains sensitive action keywords ({words})", 12))
    if features["hostname_entropy"] >= 4.2:
        score += 10
        reasons.append(("Domain name has unusually random/high-entropy characters", 10))
    if features["url_length"] >= 90:
        score += 6
        reasons.append(("URL is unusually long, which can hide malicious parameters", 6))
    if features["double_slash_redirect"]:
        score += 6
        reasons.append(("Path contains an embedded redirect pattern", 6))

    return min(score, 100), reasons


def analyze_url(raw_url: str) -> dict:
    extracted = extract_url_features(raw_url)
    features, meta = extracted["features"], extracted["meta"]

    rule_score, rule_reasons = _rule_based_score(features, meta)

    ml_probability = None
    bundle = _load_model()
    if bundle:
        vec = [[features[k] for k in bundle["feature_order"]]]
        proba = bundle["model"].predict_proba(vec)[0]
        # class 1 = phishing
        ml_probability = float(proba[1]) * 100

    # Threat intel (best-effort, offline-safe)
    intel_result = threat_intel.check_url(meta["normalized_url"])

    # ---- Ensemble ----
    if ml_probability is not None:
        combined = 0.55 * rule_score + 0.45 * ml_probability
    else:
        combined = rule_score

    if intel_result and intel_result.get("flagged"):
        combined = max(combined, 88)
        rule_reasons.append((f"Flagged by {intel_result['source']} threat intelligence", 30))
    elif intel_result and intel_result.get("checked") and not intel_result.get("flagged"):
        combined = max(0, combined - 5)

    combined = round(min(combined, 100), 1)

    explanation = [r for r, _ in sorted(rule_reasons, key=lambda x: -x[1])]
    if not explanation:
        explanation = ["No known phishing indicators detected in the URL structure."]

    factors = [{"label": r, "weight": w, "category": "url"} for r, w in rule_reasons]

    return {
        "risk_score": combined,
        "rule_score": rule_score,
        "ml_probability": ml_probability,
        "explanation": explanation,
        "factors": factors,
        "details": {
            "hostname": meta["hostname"],
            "tld": meta["tld"],
            "normalized_url": meta["normalized_url"],
            "features": features,
            "threat_intel": intel_result,
        },
    }
