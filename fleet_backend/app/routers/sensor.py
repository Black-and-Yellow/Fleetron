"""Sensor data ingestion router."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.schemas import SensorDataCreate, SensorIngestionResponse, SensorDataResponse
from app.services.sensor_processing import save_sensor_data, verify_vehicle_exists, convert_sensor_to_dict, get_latest_sensor_data
from app.services.predictions import create_prediction_from_sensor

router = APIRouter(tags=["Sensor Data"])


@router.post("/sensor-data", response_model=SensorIngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_sensor_data(sensor_data: SensorDataCreate, request: Request, db: Session = Depends(get_db)):
    """
    Ingest sensor data, run ML predictions, and return results.
    
    This endpoint:
    1. Validates vehicle exists
    2. Saves sensor data to database
    3. Runs ML predictions (failure prediction + anomaly detection)
    4. Saves prediction results
    5. Broadcasts update via WebSocket
    6. Returns combined response
    """
    # Verify vehicle exists
    if not verify_vehicle_exists(db, sensor_data.vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {sensor_data.vehicle_id} not found"
        )
    
    # Save sensor data
    db_sensor = save_sensor_data(db, sensor_data)
    
    # Convert to dict for ML processing
    sensor_dict = convert_sensor_to_dict(db_sensor)
    
    # Run predictions and save
    prediction = create_prediction_from_sensor(db, sensor_data.vehicle_id, sensor_dict)
    
    # Build response
    response = SensorIngestionResponse(
        sensor_data_id=db_sensor.id,
        prediction_id=prediction.id,
        vehicle_id=sensor_data.vehicle_id,
        failure=prediction.failure_prediction,
        confidence=prediction.failure_confidence,
        anomaly=bool(prediction.anomaly_flag),
        iso_score=prediction.iso_score,
        message=prediction.message,
        timestamp=prediction.timestamp
    )
    
    # Broadcast update to WebSocket clients
    try:
        # Get the connection manager from app state
        manager = request.app.state.ws_manager
        await manager.broadcast({
            "type": "sensor_update",
            "vehicle_id": sensor_data.vehicle_id,
            "sensor_data": {
                "speed": sensor_data.speed,
                "battery": sensor_data.battery,
                "gps_lat": sensor_data.gps_lat,
                "gps_lon": sensor_data.gps_lon,
                "temp_motor": sensor_data.temp_motor,
                "timestamp": db_sensor.timestamp.isoformat()
            },
            "prediction": {
                "failure": prediction.failure_prediction,
                "confidence": prediction.failure_confidence,
                "anomaly": bool(prediction.anomaly_flag),
                "message": prediction.message
            }
        })
    except Exception as e:
        print(f"WebSocket broadcast error: {e}")
    
    return response


@router.get("/vehicles/{vehicle_id}/latest-sensor", response_model=SensorDataResponse)
def get_vehicle_latest_sensor(vehicle_id: int, db: Session = Depends(get_db)):
    """Get the latest sensor data for a specific vehicle."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    # Get latest sensor data
    sensor_data = get_latest_sensor_data(db, vehicle_id)
    
    if not sensor_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sensor data found for vehicle {vehicle_id}"
        )
    
    return sensor_data
