"""
Seeds the database with realistic demo scan history by running the REAL
analysis engine (not fake hardcoded rows) against a curated set of
known-safe, suspicious, and malicious-style examples. This lets the
dashboard/charts look populated immediately for an offline hackathon demo,
while proving the engine's own scoring end-to-end.

Run from the backend/ directory:
    python seed_data.py
"""
import random
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, init_db
from app.models import Scan, ScanType, Verdict
from app.engine.url_analyzer import analyze_url
from app.engine.message_analyzer import analyze_message
from app.engine.file_analyzer import analyze_file
from app.engine.risk_scorer import build_result

random.seed(7)

DEMO_URLS = [
    "https://www.google.com/search?q=cybersecurity",
    "https://github.com/anthropics/claude-code",
    "https://en.wikipedia.org/wiki/Phishing",
    "https://www.iimtu.ac.in/devhack2026",
    "https://accounts.google.com/signin",
    "http://paypal-secure-verify.tk/login/confirm",
    "http://192.168.44.201/hdfcbank/login.php",
    "http://apple.id-locked-verify.cf/unlock",
    "https://bit.ly/3xJ9kLm?login=chase&id=88213aa9",
    "http://amazon-refund-center.top/claim",
    "http://secure.microsoft0ffice365-update.com/reset",
    "https://www.netflix.com/browse",
    "http://xn--paypa1-verify-9db.tk/webscr",
    "https://www.linkedin.com/in/demo-user",
    "http://irs-tax-refund-2026.gq/verify-ssn",
]

DEMO_MESSAGES = [
    ("Hi team, the sprint review is moved to 4pm tomorrow, see you in the usual room.", "email", "manager@company.com"),
    ("URGENT: Your Netflix payment failed. Update your billing details immediately to avoid service interruption: netflix-billing-update.com", "email", "support@netflix-billing-update.com"),
    ("Your bank account has been locked due to suspicious activity. Please confirm your password and OTP to unlock it right away.", "sms", "+1-202-555-0199"),
    ("Congratulations! You have won a $1000 Amazon gift card. Claim your prize now before it expires, click the link and enter your card details.", "whatsapp", None),
    ("Thanks for your order! Your package has shipped and is expected to arrive Thursday.", "email", "orders@amazon.com"),
    ("Security Alert: Someone tried to log into your account from Russia. Confirm it was you by entering your password below.", "email", "security-alert@mailservice.com"),
    ("Reminder: your dentist appointment is confirmed for next Tuesday at 3:30 PM.", "sms", None),
    ("Dear Customer, your account has been suspended. Verify your identity now by clicking here or it will be permanently closed within 24 hours.", "email", "alerts@paypal-secure-verify.tk"),
]

DEMO_FILES = [
    ("quarterly_report.pdf", b"%PDF-1.4\n%demo pdf content for scanning purposes\n%%EOF"),
    ("invoice_payment.pdf.exe", b"MZ" + bytes(200)),
    ("family_photo.png", b"\x89PNG\r\n\x1a\n" + bytes(300)),
    ("project_notes.txt", b"Meeting notes: discussed roadmap for Q3 and hiring plan." * 5),
    ("setup_installer.exe", b"MZ" + bytes([random.randint(0, 255) for _ in range(4000)])),
    ("resume_update_2026.zip", b"PK\x03\x04" + bytes(150)),
]


def run():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Scan).count() > 0:
            print("Database already has scan history — skipping seed to avoid duplicates.")
            print("(Delete the DB / table and re-run if you want a fresh seed.)")
            return

        now = datetime.now(timezone.utc)
        all_rows = []

        for url in DEMO_URLS:
            out = analyze_url(url)
            result = build_result("url", url, out)
            all_rows.append(("url", url, None, result, "heuristic+ml"))

        for content, channel, sender in DEMO_MESSAGES:
            out = analyze_message(content, channel=channel, sender=sender)
            excerpt = content[:200]
            result = build_result("message", excerpt, out)
            all_rows.append(("message", excerpt, None, result, "heuristic+ml"))

        for filename, content in DEMO_FILES:
            out = analyze_file(filename, content)
            result = build_result("file", filename, out)
            all_rows.append(("file", filename, out["details"]["sha256"], result, "heuristic"))

        random.shuffle(all_rows)
        for i, (scan_type, target, target_hash, result, source) in enumerate(all_rows):
            # Spread timestamps realistically across the last 7 days
            days_ago = random.randint(0, 6)
            hours_ago = random.randint(0, 23)
            created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=random.randint(0, 59))

            scan = Scan(
                scan_type=ScanType(scan_type),
                target=target,
                target_hash=target_hash,
                verdict=Verdict(result["verdict"]),
                risk_score=result["risk_score"],
                explanation=result["explanation"],
                details=result["details"],
                source=source,
                client_ip="203.0.113." + str(10 + i % 200),
                created_at=created_at,
            )
            db.add(scan)

        db.commit()
        print(f"Seeded {len(all_rows)} realistic demo scans using the live analysis engine.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
