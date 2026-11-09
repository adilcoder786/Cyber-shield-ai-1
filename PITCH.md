# CyberShield AI — 3-Minute Pitch

**DevHack IIMTU 2026 — Build for Impact**

A ready-to-rehearse spoken script (~450 words ≈ 3 minutes at a natural pace),
plus a slide-by-slide outline if your team wants to turn this into a deck.
Timings are guidelines — practice it twice and adjust to your own pace.

---

## The script

### 0:00 – 0:20 — Hook

> "Every 39 seconds, someone falls for a phishing attack. Not because
> they're careless — because a scam link, a fake bank text, or a disguised
> attachment looks *exactly* like the real thing. There's no easy way for a
> normal person to check before they click. So we built one."

### 0:20 – 0:50 — The problem

> "Phishing is the number one entry point for breaches and ransomware
> worldwide. The tools that exist — enterprise threat intelligence,
> antivirus suites — are built for security teams, not for a student
> checking a scholarship email, or a parent checking a 'bank alert' text.
> There's a gap between 'this feels off' and actually knowing *why*, and
> that gap is where people get caught."

### 0:50 – 2:10 — The solution + live demo (the core of your pitch)

> "That's CyberShield AI — a platform that scans **URLs, messages, and
> files**, and gives you a Safe, Suspicious, or Malicious verdict with a
> 0-to-100 risk score, in seconds. And critically — it explains *why*."

*(Switch to the live demo here — walk through exactly these four screens.)*

1. **Dashboard** (10s): "Here's our live threat dashboard — every scan we've
   run, verdict breakdowns, and trend data, in real time."
2. **URL Scanner** (20s): Click the *"Phishing example"* button →
   "This looks like PayPal, but our engine catches the brand impersonation,
   the risky domain extension, and the login-page keywords — 92 out of 100,
   flagged malicious, and it tells you exactly why, not just a red X."
3. **Message Analyzer** (20s): Click *"Prize scam"* → "This one's a fake
   prize text. Our NLP model catches the urgency language and the request
   for card details — and it automatically pulls out any links inside the
   message and scans those too."
4. **File Analyzer** (20s): Download the *"Disguised file"* sample, then
   upload it → "This file is literally named `invoice.pdf` but it's an
   executable underneath — we catch that by reading the actual file bytes,
   not just trusting the filename. That's a real malware trick, and we
   catch it in under a second."

> "Under the hood, it's a rule-based engine for transparency, blended with
> trained machine learning models for pattern recognition — so you get both
> explainability *and* the ability to catch things a fixed rulebook would
> miss."

### 2:10 – 2:40 — Why it's different / technical credibility

> "This isn't a mockup — it's a full working stack: React frontend, FastAPI
> backend, a MySQL database, and real scikit-learn models we trained
> ourselves. It runs completely offline, which matters here today with
> venue wifi — but it's also wired to plug into Google Safe Browsing and
> VirusTotal for live threat intelligence the moment you add an API key.
> No code changes, just a switch flip."

### 2:40 – 3:00 — Impact and close

> "Phishing doesn't discriminate by technical skill — it just needs one
> click. CyberShield AI puts a second opinion in everyone's pocket: not
> just 'is this dangerous,' but 'here's exactly why, in plain English.'
> That's CyberShield AI — built for impact, built to keep people safe.
> Thank you."

---

## Slide outline (if you want a deck)

| # | Slide | Content |
|---|---|---|
| 1 | Title | CyberShield AI — AI-Powered Phishing & Threat Detection · DevHack IIMTU 2026 |
| 2 | The problem | 1 stat on phishing's role in breaches + "no easy way to check before you click" |
| 3 | The solution | 3 icons: URL · Message · File → one verdict, one score, one explanation |
| 4 | Live demo | (switch to the actual app — this slide is just a placeholder/divider) |
| 5 | How it works | Simple pipeline diagram: Input → Rule Engine + ML Model → Threat Intel (optional) → Verdict |
| 6 | Tech stack | React · FastAPI · MySQL · scikit-learn · Google Safe Browsing / VirusTotal |
| 7 | What makes it real | "Fully working MVP" — trained models, live database, working API, not a mockup |
| 8 | Impact | Who benefits: students, families, small teams, anyone without a security team |
| 9 | Thank you / Q&A | Team name, repo link, contact |

## Anticipated judge questions (prepare 1–2 sentence answers)

- **"How accurate is the ML model?"** → It's trained on synthetic,
  pattern-based data for offline demo purposes (100% test accuracy on that
  synthetic set), and it's designed to be retrained on a real labeled
  dataset (PhishTank, a SOC's own logs) without any code changes —
  `train_model.py` is dataset-agnostic.
- **"What stops someone from gaming the rules?"** → The rule engine is
  blended with an ML model precisely so novel phishing patterns that don't
  match a fixed rule still get caught by the learned model, and vice versa.
- **"Does this replace antivirus?"** → No — it's a fast, explainable first
  line of defense for links/messages/files *before* you commit to opening
  them, complementary to (and integrable with) existing AV/threat-intel
  tools like VirusTotal.
- **"Why is it safe to demo offline?"** → Every external API call
  (threat intel) is wrapped with a timeout and automatic fallback to the
  offline heuristic + ML engine — nothing breaks without internet.
