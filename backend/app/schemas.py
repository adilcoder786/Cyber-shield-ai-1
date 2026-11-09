"""
Pydantic schemas for request validation and response serialization.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ---------- Requests ----------

class UrlScanRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048, examples=["http://paypa1-verify.tk/login"])

    @field_validator("url")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        return v


class MessageScanRequest(BaseModel):
    content: str = Field(..., min_length=3, max_length=20000)
    channel: Optional[str] = Field(default="email", examples=["email", "sms", "whatsapp", "other"])
    sender: Optional[str] = Field(default=None, max_length=320)

    @field_validator("content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


# ---------- Responses ----------

class RiskFactor(BaseModel):
    label: str
    weight: float
    category: str  # e.g. "url", "content", "reputation", "file"


class ScanResult(BaseModel):
    id: Optional[int] = None
    scan_type: str
    target: str
    verdict: str
    risk_score: float
    confidence: float
    explanation: List[str]
    factors: List[RiskFactor] = []
    details: Optional[Dict[str, Any]] = None
    engine_version: str = "1.0.0"
    source: str = "heuristic+ml"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanHistoryItem(BaseModel):
    id: int
    scan_type: str
    target: str
    verdict: str
    risk_score: float
    explanation: List[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedHistory(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ScanHistoryItem]


class StatsSummary(BaseModel):
    total_scans: int
    safe_count: int
    suspicious_count: int
    malicious_count: int
    avg_risk_score: float
    scans_by_type: Dict[str, int]
    scans_last_7_days: List[Dict[str, Any]]
    top_threat_indicators: List[Dict[str, Any]]
