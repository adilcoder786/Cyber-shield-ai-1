"""
Threat-intelligence integrations (Google Safe Browsing, VirusTotal).

Design goal: NEVER break the demo. If an API key is missing, the service is
unreachable, or the request times out, every function returns a safe
"not checked" result instead of raising — the platform silently falls back
to its offline heuristic + ML engine. This is what lets CyberShield AI run
fully offline during a hackathon demo, while still being wired for real
threat-intel in a production deployment.
"""
import requests
from app.config import settings

TIMEOUT_SECONDS = 4


def check_url(url: str) -> dict:
    """
    Checks a URL against Google Safe Browsing (if configured).
    Returns {"checked": bool, "flagged": bool, "source": str, "detail": str|None}
    """
    if not settings.GOOGLE_SAFE_BROWSING_API_KEY:
        return {"checked": False, "flagged": False, "source": "google_safe_browsing", "detail": "no_api_key"}

    try:
        endpoint = (
            "https://safebrowsing.googleapis.com/v4/threatMatches:find"
            f"?key={settings.GOOGLE_SAFE_BROWSING_API_KEY}"
        )
        payload = {
            "client": {"clientId": "cybershield-ai", "clientVersion": "1.0.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        resp = requests.post(endpoint, json=payload, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        matches = resp.json().get("matches", [])
        return {
            "checked": True,
            "flagged": len(matches) > 0,
            "source": "google_safe_browsing",
            "detail": matches[0]["threatType"] if matches else None,
        }
    except Exception as exc:  # network error, timeout, quota, etc.
        return {"checked": False, "flagged": False, "source": "google_safe_browsing", "detail": f"unavailable: {exc.__class__.__name__}"}


def check_file_hash(sha256_hash: str) -> dict:
    """Checks a file's SHA-256 hash against VirusTotal (if configured)."""
    if not settings.VIRUSTOTAL_API_KEY:
        return {"checked": False, "flagged": False, "source": "virustotal", "detail": "no_api_key"}

    try:
        resp = requests.get(
            f"https://www.virustotal.com/api/v3/files/{sha256_hash}",
            headers={"x-apikey": settings.VIRUSTOTAL_API_KEY},
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code == 404:
            return {"checked": True, "flagged": False, "source": "virustotal", "detail": "not_previously_seen"}
        resp.raise_for_status()
        stats = resp.json()["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0) + stats.get("suspicious", 0)
        return {
            "checked": True,
            "flagged": malicious > 0,
            "source": "virustotal",
            "detail": f"{malicious} engines flagged this file",
        }
    except Exception as exc:
        return {"checked": False, "flagged": False, "source": "virustotal", "detail": f"unavailable: {exc.__class__.__name__}"}
