from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UrlScanRequest, ScanResult
from app.engine.url_analyzer import analyze_url
from app.engine.risk_scorer import build_result
from app.models import Scan, ScanType, Verdict

router = APIRouter(prefix="/api/scan", tags=["URL Scanner"])


@router.post("/url", response_model=ScanResult, summary="Scan a URL/website for phishing risk")
def scan_url(payload: UrlScanRequest, request: Request, db: Session = Depends(get_db)):
    engine_output = analyze_url(payload.url)
    result = build_result("url", payload.url, engine_output)

    scan = Scan(
        scan_type=ScanType.url,
        target=payload.url[:2048],
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
