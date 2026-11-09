"""
ORM models. A single `scans` table stores every scan (URL / message / file),
which keeps history + stats queries simple while remaining normalized enough
for a hackathon-grade production MVP.
"""
import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Enum
from sqlalchemy.sql import func

from app.database import Base


class ScanType(str, enum.Enum):
    url = "url"
    message = "message"
    file = "file"


class Verdict(str, enum.Enum):
    safe = "safe"
    suspicious = "suspicious"
    malicious = "malicious"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(Enum(ScanType), nullable=False, index=True)

    # What was scanned (url string, message excerpt, or filename)
    target = Column(String(2048), nullable=False)
    target_hash = Column(String(64), index=True, nullable=True)  # sha256, for files

    verdict = Column(Enum(Verdict), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)  # 0-100

    # Human-readable bullet-point reasons ["Domain registered 3 days ago", ...]
    explanation = Column(JSON, nullable=False, default=list)

    # Raw signal breakdown used for charts / audits, e.g. {"url_features": {...}}
    details = Column(JSON, nullable=True)

    engine_version = Column(String(32), default="1.0.0")
    source = Column(String(32), default="heuristic+ml")  # or "threat_intel"
    client_ip = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "scan_type": self.scan_type.value if hasattr(self.scan_type, "value") else self.scan_type,
            "target": self.target,
            "verdict": self.verdict.value if hasattr(self.verdict, "value") else self.verdict,
            "risk_score": self.risk_score,
            "explanation": self.explanation,
            "details": self.details,
            "engine_version": self.engine_version,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
