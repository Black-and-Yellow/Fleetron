"""Maintenance logs router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import MaintenanceLog
from app.schemas import MaintenanceLogCreate, MaintenanceLogResponse
from app.services.sensor_processing import verify_vehicle_exists

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post("/", response_model=MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_log(log: MaintenanceLogCreate, db: Session = Depends(get_db)):
    """Create a new maintenance log entry."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, log.vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {log.vehicle_id} not found"
        )
    
    # Create maintenance log
    db_log = MaintenanceLog(
        vehicle_id=log.vehicle_id,
        issue_type=log.issue_type,
        severity=log.severity,
        predicted_by_ai=log.predicted_by_ai,
        status=log.status
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


@router.get("/{vehicle_id}", response_model=List[MaintenanceLogResponse])
def get_vehicle_maintenance_logs(vehicle_id: int, db: Session = Depends(get_db)):
    """Get all maintenance logs for a specific vehicle."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    # Get maintenance logs
    logs = db.query(MaintenanceLog).filter(
        MaintenanceLog.vehicle_id == vehicle_id
    ).order_by(MaintenanceLog.created_at.desc()).all()
    
    return logs
