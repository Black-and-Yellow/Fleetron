"""Predictions router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PredictionResponse
from app.services.predictions import get_latest_prediction
from app.services.sensor_processing import verify_vehicle_exists

router = APIRouter(prefix="/vehicles", tags=["Predictions"])


@router.get("/{vehicle_id}/predictions/latest", response_model=PredictionResponse)
def get_vehicle_latest_prediction(vehicle_id: int, db: Session = Depends(get_db)):
    """Get the latest prediction for a specific vehicle."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    # Get latest prediction
    prediction = get_latest_prediction(db, vehicle_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for vehicle {vehicle_id}"
        )
    
    return prediction
