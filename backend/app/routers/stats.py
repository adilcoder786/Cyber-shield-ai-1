from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Scan
from app.schemas import StatsSummary

router = APIRouter(prefix="/api/stats", tags=["Threat Statistics"])


@router.get("/summary", response_model=StatsSummary, summary="Dashboard-level aggregate threat statistics")
def stats_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Scan.id)).scalar() or 0
    avg_score = db.query(func.avg(Scan.risk_score)).scalar() or 0.0

    verdict_counts = dict(
        db.query(Scan.verdict, func.count(Scan.id)).group_by(Scan.verdict).all()
    )
    # normalize keys (Enum -> str)
    verdict_counts = {(k.value if hasattr(k, "value") else k): v for k, v in verdict_counts.items()}

    type_counts = dict(
        db.query(Scan.scan_type, func.count(Scan.id)).group_by(Scan.scan_type).all()
    )
    type_counts = {(k.value if hasattr(k, "value") else k): v for k, v in type_counts.items()}

    # last 7 days trend (Python-side grouping for cross-DB portability: MySQL + SQLite)
    since = datetime.now(timezone.utc) - timedelta(days=7)
    recent = db.query(Scan.created_at, Scan.verdict).filter(Scan.created_at >= since).all()
    day_buckets = {}
    for i in range(6, -1, -1):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        day_buckets[day] = {"date": day, "safe": 0, "suspicious": 0, "malicious": 0}
    for created_at, verdict in recent:
        if not created_at:
            continue
        day = created_at.strftime("%Y-%m-%d")
        v = verdict.value if hasattr(verdict, "value") else verdict
        if day in day_buckets:
            day_buckets[day][v] = day_buckets[day].get(v, 0) + 1

    # top threat indicators: count explanation phrase frequency across last 200 scans
    recent_explanations = (
        db.query(Scan.explanation)
        .order_by(Scan.created_at.desc())
        .limit(200)
        .all()
    )
    counter = Counter()
    for (exp_list,) in recent_explanations:
        if not exp_list:
            continue
        for reason in exp_list:
            counter[reason] += 1
    top_indicators = [{"indicator": k, "count": v} for k, v in counter.most_common(8)]

    return {
        "total_scans": total,
        "safe_count": verdict_counts.get("safe", 0),
        "suspicious_count": verdict_counts.get("suspicious", 0),
        "malicious_count": verdict_counts.get("malicious", 0),
        "avg_risk_score": round(float(avg_score), 1),
        "scans_by_type": {
            "url": type_counts.get("url", 0),
            "message": type_counts.get("message", 0),
            "file": type_counts.get("file", 0),
        },
        "scans_last_7_days": list(day_buckets.values()),
        "top_threat_indicators": top_indicators,
    }
