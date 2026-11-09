from pathlib import Path

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ScanResult
from app.engine.file_analyzer import analyze_file
from app.engine.risk_scorer import build_result
from app.models import Scan, ScanType, Verdict
from app.config import settings

router = APIRouter(prefix="/api/scan", tags=["File Analyzer"])

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/file", response_model=ScanResult, summary="Scan an uploaded file for risk indicators")
async def scan_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    engine_output = analyze_file(file.filename, content)
    result = build_result("file", file.filename, engine_output)

    scan = Scan(
        scan_type=ScanType.file,
        target=file.filename[:2048],
        target_hash=engine_output["details"]["sha256"],
        verdict=Verdict(result["verdict"]),
        risk_score=result["risk_score"],
        explanation=result["explanation"],
        details=result["details"],
        source="heuristic",
        client_ip=request.client.host if request.client else None,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    result["id"] = scan.id
    result["created_at"] = scan.created_at
    return result
