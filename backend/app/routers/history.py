from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Scan
from app.schemas import PaginatedHistory

router = APIRouter(prefix="/api/history", tags=["Scan History"])


@router.get("", response_model=PaginatedHistory, summary="List past scans (paginated, filterable)")
def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    scan_type: Optional[str] = Query(None, description="url | message | file"),
    verdict: Optional[str] = Query(None, description="safe | suspicious | malicious"),
    search: Optional[str] = Query(None, description="Search within target text"),
    db: Session = Depends(get_db),
):
    q = db.query(Scan)
    if scan_type:
        q = q.filter(Scan.scan_type == scan_type)
    if verdict:
        q = q.filter(Scan.verdict == verdict)
    if search:
        q = q.filter(Scan.target.ilike(f"%{search}%"))

    total = q.count()
    items = (
        q.order_by(desc(Scan.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [i.to_dict() for i in items],
    }


@router.get("/{scan_id}", summary="Get full detail for a single scan")
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan.to_dict()


@router.delete("/{scan_id}", summary="Delete a scan record")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    db.delete(scan)
    db.commit()
    return {"deleted": True, "id": scan_id}
