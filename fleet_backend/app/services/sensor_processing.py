"""Sensor data processing service."""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import SensorData, Vehicle
from app.schemas import SensorDataCreate
from typing import Dict, Any


def save_sensor_data(db: Session, sensor_data: SensorDataCreate) -> SensorData:
    """
    Save sensor data to database.
    
    Args:
        db: Database session
        sensor_data: Sensor data schema
        
    Returns:
        SensorData object
    """
    # Create sensor data record
    db_sensor = SensorData(
        vehicle_id=sensor_data.vehicle_id,
        timestamp=datetime.utcnow(),
        gps_lat=sensor_data.gps_lat,
        gps_lon=sensor_data.gps_lon,
        speed=sensor_data.speed,
        battery=sensor_data.battery,
        acc_x=sensor_data.acc_x,
        acc_y=sensor_data.acc_y,
        acc_z=sensor_data.acc_z,
        temp_motor=sensor_data.temp_motor,
        raw_payload=sensor_data.raw_payload
    )
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor


def get_latest_sensor_data(db: Session, vehicle_id: int) -> SensorData:
    """
    Get the latest sensor data for a vehicle.
    
    Args:
        db: Database session
        vehicle_id: Vehicle ID
        
    Returns:
        Latest SensorData object or None
    """
    return db.query(SensorData).filter(
        SensorData.vehicle_id == vehicle_id
    ).order_by(SensorData.timestamp.desc()).first()


def convert_sensor_to_dict(sensor: SensorData) -> Dict[str, Any]:
    """
    Convert SensorData object to dictionary for ML processing.
    
    Args:
        sensor: SensorData object
        
    Returns:
        Dictionary with sensor values
    """
    return {
        "vehicle_id": sensor.vehicle_id,
        "gps_lat": sensor.gps_lat,
        "gps_lon": sensor.gps_lon,
        "speed": sensor.speed,
        "battery": sensor.battery,
        "acc_x": sensor.acc_x,
        "acc_y": sensor.acc_y,
        "acc_z": sensor.acc_z,
        "temp_motor": sensor.temp_motor
    }


def verify_vehicle_exists(db: Session, vehicle_id: int) -> bool:
    """
    Check if vehicle exists in database.
    
    Args:
        db: Database session
        vehicle_id: Vehicle ID
        
    Returns:
        True if vehicle exists, False otherwise
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    return vehicle is not None
