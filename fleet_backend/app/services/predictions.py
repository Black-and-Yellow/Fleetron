"""Prediction service for ML operations."""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Prediction, MaintenanceLog
from app.ml.utils import predict_all
from typing import Dict, Any


def create_prediction_from_sensor(
    db: Session,
    vehicle_id: int,
    sensor_data: Dict[str, Any]
) -> Prediction:
    """
    Run ML predictions and save to database.
    
    Args:
        db: Database session
        vehicle_id: Vehicle ID
        sensor_data: Sensor data dictionary
        
    Returns:
        Prediction object
    """
    # Run all predictions
    pred_result = predict_all(sensor_data)
    
    # Create prediction record
    prediction = Prediction(
        vehicle_id=vehicle_id,
        timestamp=datetime.utcnow(),
        failure_prediction=pred_result["failure"],
        failure_confidence=pred_result["confidence"],
        anomaly_flag=pred_result["anomaly_flag"],
        iso_score=pred_result["iso_score"],
        message=pred_result["message"]
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    # If critical failure predicted, create maintenance log
    if pred_result["failure"] == 1 and pred_result["confidence"] > 0.7:
        create_maintenance_from_prediction(db, vehicle_id, pred_result)
    
    return prediction


def create_maintenance_from_prediction(
    db: Session,
    vehicle_id: int,
    pred_result: Dict[str, Any]
):
    """
    Create maintenance log when critical failure is predicted.
    
    Args:
        db: Database session
        vehicle_id: Vehicle ID
        pred_result: Prediction result dictionary
    """
    # Determine severity based on confidence
    confidence = pred_result.get("confidence", 0.5)
    if confidence > 0.9:
        severity = "critical"
    elif confidence > 0.7:
        severity = "high"
    else:
        severity = "medium"
    
    # Create maintenance log
    maintenance = MaintenanceLog(
        vehicle_id=vehicle_id,
        issue_type="motor_failure",
        severity=severity,
        predicted_by_ai=True,
        status="pending"
    )
    
    db.add(maintenance)
    db.commit()


def get_latest_prediction(db: Session, vehicle_id: int) -> Prediction:
    """
    Get the latest prediction for a vehicle.
    
    Args:
        db: Database session
        vehicle_id: Vehicle ID
        
    Returns:
        Latest Prediction object or None
    """
    return db.query(Prediction).filter(
        Prediction.vehicle_id == vehicle_id
    ).order_by(Prediction.timestamp.desc()).first()
