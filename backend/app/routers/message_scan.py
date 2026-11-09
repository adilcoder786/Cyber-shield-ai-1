from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MessageScanRequest, ScanResult
from app.engine.message_analyzer import analyze_message
from app.engine.risk_scorer import build_result
from app.models import Scan, ScanType, Verdict

router = APIRouter(prefix="/api/scan", tags=["Message Analyzer"])


@router.post("/message", response_model=ScanResult, summary="Scan an email/SMS/message for phishing risk")
def scan_message(payload: MessageScanRequest, request: Request, db: Session = Depends(get_db)):
    engine_output = analyze_message(payload.content, channel=payload.channel, sender=payload.sender)
    excerpt = payload.content.strip().replace("\n", " ")[:200]
    result = build_result("message", excerpt, engine_output)

    scan = Scan(
        scan_type=ScanType.message,
        target=excerpt,
        verdict=Verdict(result["verdict"]),
        risk_score=result["risk_score"],
        explanation=result["explanation"],
        details=result["details"],
        source="heuristic+ml" if engine_output.get("ml_probability") is not None else "heuristic",
        client_ip=request.client.host if request.client else None,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    result["id"] = scan.id
    result["created_at"] = scan.created_at
    return result
