"""
Trains two lightweight scikit-learn models used by CyberShield AI:

1. URL phishing classifier (RandomForest) over engineered URL features.
2. Message/email phishing text classifier (TF-IDF + Logistic Regression).

Datasets are synthetically generated / hand-authored here so the whole
project can be trained and demoed fully OFFLINE, with no external dataset
downloads required (important for a hackathon environment). In production,
swap `build_url_dataset()` / `MESSAGE_SAMPLES` for a real labeled dataset
(e.g. PhishTank + Tranco top sites, or an internal SOC corpus) — the
training/serialization code does not need to change.

Run:
    python -m app.ml.train_model
"""
import random
import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from app.ml.url_features import feature_vector, FEATURE_ORDER

random.seed(42)
MODEL_DIR = Path(__file__).resolve().parent
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 1. URL DATASET (synthetic, pattern-based)
# --------------------------------------------------------------------------

LEGIT_DOMAINS = [
    "google.com", "wikipedia.org", "github.com", "nytimes.com", "amazon.com",
    "microsoft.com", "apple.com", "spotify.com", "linkedin.com", "reddit.com",
    "bbc.com", "nasa.gov", "who.int", "iimtu.ac.in", "npmjs.com", "python.org",
    "stackoverflow.com", "notion.so", "figma.com", "cloudflare.com",
    "mozilla.org", "openai.com", "anthropic.com", "netflix.com", "airbnb.com",
]
LEGIT_PATHS = ["", "/", "/about", "/docs", "/blog/2026/update", "/pricing",
               "/search?q=weather", "/user/settings", "/careers", "/help/faq"]

BRANDS = ["paypal", "apple", "microsoft", "netflix", "amazon", "chase",
          "hdfcbank", "instagram", "irs", "dhl", "linkedin", "coinbase"]
SUSPICIOUS_TLDS = ["tk", "ml", "ga", "cf", "xyz", "top", "click", "gq", "loan"]
PHISH_KEYWORDS = ["login", "verify", "secure", "account", "update-billing",
                   "confirm", "signin", "webscr", "recover-password", "unlock"]


def _rand_hex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def build_url_dataset(n_per_class=650):
    urls, labels = [], []

    # ---- legitimate URLs ----
    for _ in range(n_per_class):
        domain = random.choice(LEGIT_DOMAINS)
        path = random.choice(LEGIT_PATHS)
        scheme = "https"
        url = f"{scheme}://{domain}{path}"
        urls.append(url)
        labels.append(0)

    # ---- phishing-style URLs (rule-generated patterns) ----
    for _ in range(n_per_class):
        pattern = random.randint(0, 5)
        brand = random.choice(BRANDS)
        kw = random.choice(PHISH_KEYWORDS)
        tld = random.choice(SUSPICIOUS_TLDS)

        if pattern == 0:
            # brand + hyphen + suspicious tld
            url = f"http://{brand}-{kw}.{tld}/{_rand_hex(6)}"
        elif pattern == 1:
            # raw IP address host
            ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
            url = f"http://{ip}/{brand}/{kw}.php"
        elif pattern == 2:
            # subdomain stuffing to fake the brand
            url = f"http://{brand}.{kw}.secure-{_rand_hex(4)}.com/login"
        elif pattern == 3:
            # @ symbol trick
            url = f"http://{brand}.com@{_rand_hex(5)}.{tld}/{kw}"
        elif pattern == 4:
            # punycode homograph
            url = f"http://xn--{_rand_hex(8)}.{tld}/{kw}-{brand}"
        else:
            # long confusing query string shortener-style
            url = f"http://bit.ly/{_rand_hex(7)}?{kw}={brand}&id={_rand_hex(10)}"

        urls.append(url)
        labels.append(1)

    return urls, labels


def train_url_model():
    urls, labels = build_url_dataset()
    X = [feature_vector(u) for u in urls]
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )

    clf = RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"
    )
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"[url_model] accuracy={acc:.4f} f1={f1:.4f} n_train={len(X_train)} n_test={len(X_test)}")

    joblib.dump({"model": clf, "feature_order": FEATURE_ORDER}, MODEL_DIR / "url_model.joblib")
    return acc, f1


# --------------------------------------------------------------------------
# 2. MESSAGE / EMAIL TEXT DATASET (hand-authored samples)
# --------------------------------------------------------------------------

PHISHING_MESSAGES = [
    "Dear Customer, your account has been suspended. Verify your identity now by clicking here or it will be permanently closed within 24 hours.",
    "URGENT: Your Netflix payment failed. Update your billing details immediately to avoid service interruption: netflix-billing-update.com",
    "Congratulations! You have won a $1000 Amazon gift card. Claim your prize now before it expires, click the link and enter your card details.",
    "Your bank account has been locked due to suspicious activity. Please confirm your password and OTP to unlock it right away.",
    "IRS Notice: You owe back taxes. Failure to respond within 48 hours will result in legal action. Pay now via the secure link.",
    "We detected unusual sign-in activity on your Apple ID. Verify your account now or it will be disabled.",
    "Your parcel could not be delivered. Pay a small customs fee of $2.99 to reschedule delivery immediately.",
    "Final reminder: your subscription will auto-renew for $499. Cancel now by confirming your card number and CVV.",
    "Hi, this is HR. Please review the attached urgent salary revision document and enter your employee login to access it.",
    "Your PayPal account is limited. Click here to verify your information and restore full access within 24 hours.",
    "Security Alert: Someone tried to log into your account from Russia. Confirm it was you by entering your password below.",
    "You have a pending refund of $350. Provide your bank account and routing number to receive the funds today.",
    "Dear user, your mailbox has exceeded its storage limit. Click here and login with your email credentials to upgrade instantly.",
    "WINNER!!! You've been selected for a free iPhone 17. Confirm your shipping address and pay a $5 processing fee now.",
    "Action required: Update your Microsoft 365 password within 12 hours or your account access will be permanently revoked.",
    "This is your bank. We noticed a large withdrawal attempt. Verify your identity immediately by replying with your PIN.",
    "Your document has been shared via a secure portal. Sign in with your work email and password to view it now.",
    "Attention: Your electricity bill payment failed. Avoid disconnection today, pay immediately using the link below.",
    "Congratulations, your number has won the UK National Lottery. Send your bank details to claim 850,000 GBP.",
    "We could not verify your recent order. Confirm your card details within 24 hours to avoid order cancellation.",
    "Your WhatsApp account will be deactivated. Verify now by entering the OTP sent to you and forwarding it to us.",
    "Dear valued customer, unusual activity detected on your Chase account. Verify now to avoid permanent suspension.",
    "You have an urgent voicemail regarding your student loan forgiveness. Enter your SSN to check your eligibility instantly.",
    "Your Instagram account was reported for copyright infringement. Appeal now by logging in through this official-looking link.",
    "Job offer: Immediate hiring, $45/hr work from home. Provide your bank account details for direct deposit setup today.",
    "Final notice regarding your vehicle warranty. Call now or click the link to renew before it's too late.",
    "Your Coinbase wallet has been flagged for suspicious transactions. Verify your seed phrase to prevent account freeze.",
    "Reminder: Your domain renewal failed. Renew now with your admin credentials or lose your website permanently.",
    "Dear customer, your recent Amazon order requires payment verification. Click here and re-enter your card information.",
    "We tried to deliver a package but nobody was home. Confirm your address and pay the redelivery fee to reschedule.",
]

LEGIT_MESSAGES = [
    "Hi team, quick reminder that our sprint planning meeting is scheduled for 10am tomorrow in the main conference room.",
    "Thanks for your order! Your package has shipped and is expected to arrive on Thursday. Track it anytime from your account.",
    "Hey, are we still on for lunch this Friday? Let me know what time works best for you.",
    "Your monthly statement is now available in your online banking portal under the Statements tab.",
    "Reminder: your dentist appointment is confirmed for next Tuesday at 3:30 PM. Reply to reschedule if needed.",
    "The quarterly report has been uploaded to the shared drive. Let me know if you have any questions before the review.",
    "Welcome to the team! Your first day orientation will start at 9am in the HR office, see you then.",
    "Your flight booking is confirmed. Check-in opens 24 hours before departure on the airline's official app.",
    "Great catching up today, I'll send over the notes from our call by end of day.",
    "Your library book is due back in 3 days. You can renew it online from your library account if needed.",
    "The gym will be closed this weekend for maintenance. Regular hours resume Monday morning.",
    "Happy birthday! Hope you have a fantastic day, let's grab coffee sometime this week to celebrate.",
    "Your electricity meter reading has been recorded. No action is needed, this is just a confirmation.",
    "Attached is the agenda for tomorrow's board meeting. Please review before we meet at 2pm.",
    "Thanks for signing up for our newsletter, you'll receive updates about new blog posts once a week.",
    "The school play is next Friday at 6pm in the auditorium, we'd love to see you there.",
    "Your rent payment for this month has been received, thank you for paying on time.",
    "Just a heads up, the office wifi will be down for scheduled maintenance tonight from 11pm to midnight.",
    "Can you review the pull request I sent over? No rush, whenever you get a chance this week.",
    "Your prescription refill is ready for pickup at the pharmacy anytime after 10am today.",
    "Loved the presentation you gave today, the data visualizations really helped tell the story.",
    "The community garden meetup has been moved to Saturday morning due to the weather forecast.",
    "Here's the recipe you asked about, let me know how it turns out if you try making it this weekend.",
    "Your car service appointment is booked for next Monday at 9am, please bring the service booklet.",
    "The report you requested is attached, let me know if you'd like me to walk you through any section.",
    "Reminder that the office will be closed on Monday for the public holiday, see everyone Tuesday.",
    "Congrats on the promotion, well deserved! Let's celebrate with the team sometime this month.",
    "Your water bill for this month is now available to view in the city services portal.",
    "The train to downtown is running 10 minutes late this morning due to signal maintenance.",
    "Thanks for the feedback on the design mockups, I'll incorporate the changes and share an update tomorrow.",
]


def train_message_model():
    texts = PHISHING_MESSAGES + LEGIT_MESSAGES
    labels = [1] * len(PHISHING_MESSAGES) + [0] * len(LEGIT_MESSAGES)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(
        lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(X_train_vec, y_train)
    preds = clf.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"[message_model] accuracy={acc:.4f} f1={f1:.4f} n_train={len(X_train)} n_test={len(X_test)}")

    joblib.dump({"model": clf, "vectorizer": vectorizer}, MODEL_DIR / "message_model.joblib")
    return acc, f1


if __name__ == "__main__":
    url_acc, url_f1 = train_url_model()
    msg_acc, msg_f1 = train_message_model()
    metrics = {
        "url_model": {"accuracy": url_acc, "f1": url_f1},
        "message_model": {"accuracy": msg_acc, "f1": msg_f1},
    }
    with open(MODEL_DIR / "training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("\nModels saved to", MODEL_DIR)
    print(json.dumps(metrics, indent=2))
