"""
File risk analyzer.
Runs static, signature-free checks that are safe to perform on any uploaded
file without executing it:
  - extension risk category
  - double-extension trick detection (invoice.pdf.exe)
  - magic-byte vs. extension mismatch (spoofed file type)
  - Shannon entropy (packed/encrypted/obfuscated payloads)
  - embedded suspicious string/keyword scan
  - optional VirusTotal hash lookup (best-effort, offline-safe)
"""
import math
import re
import hashlib

from app.engine import threat_intel

HIGH_RISK_EXTENSIONS = {".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".jar",
                         ".ps1", ".msi", ".lnk", ".apk", ".com", ".hta", ".wsf"}
MEDIUM_RISK_EXTENSIONS = {".docm", ".xlsm", ".pptm", ".zip", ".rar", ".7z",
                           ".iso", ".img", ".dll"}
LOW_RISK_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt",
                        ".png", ".jpg", ".jpeg", ".gif", ".csv", ".html", ".htm"}

# (extension set, expected magic byte prefixes)
MAGIC_SIGNATURES = {
    "pdf": (b"%PDF",),
    "zip_family": (b"PK\x03\x04", b"PK\x05\x06"),  # zip, docx, xlsx, pptx, jar, apk are all zip-based
    "exe": (b"MZ",),
    "png": (b"\x89PNG",),
    "jpg": (b"\xff\xd8\xff",),
    "gif": (b"GIF8",),
    "rar": (b"Rar!\x1a\x07",),
    "ole": (b"\xd0\xcf\x11\xe0",),  # legacy .doc/.xls
}

SUSPICIOUS_CONTENT_STRINGS = [
    b"powershell", b"cmd.exe", b"wscript.shell", b"regsvr32",
    b"invoke-expression", b"iex(", b"autoopen", b"auto_open",
    b"<script", b"eval(", b"document.write(", b"createobject",
    b"downloadstring", b"bitsadmin", b"certutil -decode", b"shellexecute",
]

SUSPICIOUS_FILENAME_WORDS = ["invoice", "payment", "urgent", "receipt",
                              "statement", "unpaid", "resume_", "compensation",
                              "refund", "important_update"]


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def _detect_actual_type(data: bytes) -> str:
    for name, sigs in MAGIC_SIGNATURES.items():
        for sig in sigs:
            if data.startswith(sig):
                return name
    return "unknown"


def analyze_file(filename: str, content: bytes) -> dict:
    reasons = []
    score = 0

    lower_name = filename.lower()
    parts = lower_name.split(".")
    ext = "." + parts[-1] if len(parts) > 1 else ""
    all_exts = ["." + p for p in parts[1:]] if len(parts) > 2 else []

    # 1. Extension risk category
    if ext in HIGH_RISK_EXTENSIONS:
        score += 40
        reasons.append((f"File extension '{ext}' is executable/script-based and high-risk", 40))
    elif ext in MEDIUM_RISK_EXTENSIONS:
        score += 18
        reasons.append((f"File extension '{ext}' can contain macros or hidden payloads", 18))
    elif ext in LOW_RISK_EXTENSIONS:
        score += 2
    else:
        score += 10
        reasons.append((f"Unrecognized/uncommon file extension '{ext}'", 10))

    # 2. Double-extension trick, e.g. invoice.pdf.exe
    if len(all_exts) >= 2 and all_exts[-1] in HIGH_RISK_EXTENSIONS and all_exts[-2] in LOW_RISK_EXTENSIONS:
        score += 30
        reasons.append((f"Double file extension detected ('{all_exts[-2]}{all_exts[-1]}') — a classic disguise trick", 30))

    # 3. Suspicious filename wording
    name_hits = [w for w in SUSPICIOUS_FILENAME_WORDS if w in lower_name]
    if name_hits:
        score += 8
        reasons.append((f"Filename uses urgency/finance-bait wording ({name_hits[0]})", 8))

    # 4. Magic byte vs extension mismatch
    actual_type = _detect_actual_type(content[:16])
    mismatch = False
    if ext == ".pdf" and actual_type != "pdf":
        mismatch = True
    elif ext in {".docx", ".xlsx", ".pptx", ".zip", ".jar", ".apk"} and actual_type not in {"zip_family"}:
        mismatch = True
    elif ext in {".doc", ".xls", ".ppt"} and actual_type not in {"ole"}:
        mismatch = True
    elif ext in {".png"} and actual_type != "png":
        mismatch = True
    elif ext in {".jpg", ".jpeg"} and actual_type != "jpg":
        mismatch = True
    if actual_type == "exe" and ext not in HIGH_RISK_EXTENSIONS:
        mismatch = True
        score += 35
        reasons.append(("File content is a Windows executable (MZ header) despite a non-executable extension", 35))
    elif mismatch and actual_type != "unknown":
        score += 20
        reasons.append((f"File extension '{ext}' does not match the actual file content signature", 20))

    # 5. Entropy (packed/encrypted/obfuscated payloads tend to be very high entropy)
    entropy = round(_shannon_entropy(content[:200000]), 3)
    if entropy >= 7.5 and ext not in {".zip", ".rar", ".7z", ".jpg", ".jpeg", ".png", ".gif", ".iso"}:
        score += 15
        reasons.append((f"File has unusually high entropy ({entropy}/8.0), suggesting packing or encryption", 15))

    # 6. Suspicious embedded strings
    lowered_content = content[:2_000_000].lower()
    string_hits = [s.decode() for s in SUSPICIOUS_CONTENT_STRINGS if s in lowered_content]
    if string_hits:
        w = min(10 * len(string_hits), 35)
        score += w
        reasons.append((f"Contains suspicious embedded commands/strings ({', '.join(string_hits[:3])})", w))

    # 7. Threat intel hash lookup (best-effort)
    sha256_hash = hashlib.sha256(content).hexdigest()
    intel_result = threat_intel.check_file_hash(sha256_hash)
    if intel_result.get("flagged"):
        score = max(score, 90)
        reasons.append((f"Flagged by {intel_result['source']}: {intel_result.get('detail')}", 40))

    score = min(round(score, 1), 100)
    explanation = [r for r, _ in sorted(reasons, key=lambda x: -x[1])]
    if not explanation:
        explanation = ["No known risk indicators found in this file."]

    factors = [{"label": r, "weight": w, "category": "file"} for r, w in reasons]

    return {
        "risk_score": score,
        "explanation": explanation,
        "factors": factors,
        "details": {
            "filename": filename,
            "extension": ext,
            "detected_type": actual_type,
            "sha256": sha256_hash,
            "entropy": entropy,
            "size_bytes": len(content),
            "threat_intel": intel_result,
        },
    }
