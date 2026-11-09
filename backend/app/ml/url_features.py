"""
Deterministic feature extraction for URLs.
Used by BOTH the rule-based engine (for human-readable explanations) and the
scikit-learn model (as a numeric feature vector) so the two stay consistent.
"""
import re
import math
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "top", "xyz", "work", "click", "loan",
    "cam", "gdn", "zip", "mom", "rest", "quest", "kim", "party", "review",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "rebrand.ly", "cutt.ly", "shorturl.at", "rb.gy",
}

BRAND_KEYWORDS = [
    "paypal", "apple", "microsoft", "google", "amazon", "netflix", "bank",
    "wellsfargo", "chase", "hdfc", "icici", "sbi", "instagram", "facebook",
    "whatsapp", "outlook", "office365", "irs", "dhl", "fedex", "linkedin",
    "coinbase", "binance", "steam", "flipkart",
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "confirm", "signin",
    "webscr", "banking", "password", "suspend", "unlock", "billing",
    "recover", "invoice", "urgent", "limited", "reset",
]


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)


def extract_url_features(raw_url: str) -> dict:
    url = raw_url.strip()
    if not re.match(r"^[a-zA-Z]+://", url):
        # default to http so urlparse works consistently; flagged separately
        parse_target = "http://" + url
    else:
        parse_target = url

    parsed = urlparse(parse_target)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    full_lower = url.lower()

    labels = hostname.split(".") if hostname else []
    tld = labels[-1] if len(labels) >= 2 else ""
    domain_no_tld = ".".join(labels[:-1]) if len(labels) >= 2 else hostname

    is_ip_host = bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", hostname))
    has_at_symbol = "@" in url
    has_https = parse_target.startswith("https://")
    num_subdomains = max(len(labels) - 2, 0)
    num_hyphens = hostname.count("-")
    num_digits_domain = sum(c.isdigit() for c in hostname)
    url_length = len(url)
    is_shortener = hostname in URL_SHORTENERS
    is_punycode = "xn--" in hostname
    suspicious_tld = tld in SUSPICIOUS_TLDS

    brand_in_domain = [b for b in BRAND_KEYWORDS if b in domain_no_tld]
    # brand impersonation: brand word appears but domain isn't the real brand domain
    brand_impersonation = False
    for b in brand_in_domain:
        if domain_no_tld.replace("-", "") != b:
            brand_impersonation = True

    suspicious_words_found = [w for w in SUSPICIOUS_KEYWORDS if w in full_lower]
    num_suspicious_words = len(suspicious_words_found)

    double_slash_redirect = "//" in path
    has_port = parsed.port is not None
    entropy = _shannon_entropy(hostname)
    query_len = len(query)
    num_params = query.count("=")

    features = {
        "url_length": url_length,
        "hostname_length": len(hostname),
        "is_ip_host": int(is_ip_host),
        "has_at_symbol": int(has_at_symbol),
        "has_https": int(has_https),
        "num_subdomains": num_subdomains,
        "num_hyphens": num_hyphens,
        "num_digits_domain": num_digits_domain,
        "is_shortener": int(is_shortener),
        "is_punycode": int(is_punycode),
        "suspicious_tld": int(suspicious_tld),
        "brand_impersonation": int(brand_impersonation),
        "num_suspicious_words": num_suspicious_words,
        "double_slash_redirect": int(double_slash_redirect),
        "has_port": int(has_port),
        "hostname_entropy": round(entropy, 3),
        "query_length": query_len,
        "num_params": num_params,
        "path_length": len(path),
    }

    meta = {
        "hostname": hostname,
        "tld": tld,
        "brand_in_domain": brand_in_domain,
        "suspicious_words_found": suspicious_words_found,
        "normalized_url": parse_target,
        "had_scheme": parse_target == url,
    }
    return {"features": features, "meta": meta}


FEATURE_ORDER = [
    "url_length", "hostname_length", "is_ip_host", "has_at_symbol", "has_https",
    "num_subdomains", "num_hyphens", "num_digits_domain", "is_shortener",
    "is_punycode", "suspicious_tld", "brand_impersonation", "num_suspicious_words",
    "double_slash_redirect", "has_port", "hostname_entropy", "query_length",
    "num_params", "path_length",
]


def feature_vector(raw_url: str):
    data = extract_url_features(raw_url)["features"]
    return [data[k] for k in FEATURE_ORDER]
