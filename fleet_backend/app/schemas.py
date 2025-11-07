"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ============== Vehicle Schemas ==============
class VehicleBase(BaseModel):
    """Base vehicle schema."""
    vehicle_name: str
    model: str
    status: Optional[str] = "active"


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""
    vehicle_name: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Response schema for vehicle."""
    id: int
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Sensor Data Schemas ==============
class SensorDataBase(BaseModel):
    """Base sensor data schema."""
    vehicle_id: int
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    speed: Optional[float] = None
    battery: Optional[float] = None
    acc_x: Optional[float] = None
    acc_y: Optional[float] = None
    acc_z: Optional[float] = None
    temp_motor: Optional[float] = None
    raw_payload: Optional[Dict[str, Any]] = None


class SensorDataCreate(SensorDataBase):
    """Schema for creating sensor data entry."""
    pass


class SensorDataResponse(SensorDataBase):
    """Response schema for sensor data."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============== Prediction Schemas ==============
class PredictionBase(BaseModel):
    """Base prediction schema."""
    vehicle_id: int
    failure_prediction: int
    failure_confidence: float
    anomaly_flag: int
    iso_score: float
    message: str


class PredictionCreate(PredictionBase):
    """Schema for creating prediction."""
    pass


class PredictionResponse(PredictionBase):
    """Response schema for prediction."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class PredictionResult(BaseModel):
    """Schema for ML prediction result."""
    failure: int
    confidence: float
    anomaly: bool
    iso_score: float
    message: str
    vehicle_id: int
    timestamp: datetime


# ============== Fleet Task Schemas ==============
class FleetTaskBase(BaseModel):
    """Base fleet task schema."""
    vehicle_id: int
    task_type: str
    pickup_location: Optional[Dict[str, Any]] = None
    drop_location: Optional[Dict[str, Any]] = None
    status: Optional[str] = "assigned"
    eta: Optional[datetime] = None


class FleetTaskCreate(FleetTaskBase):
    """Schema for creating a fleet task."""
    pass


class FleetTaskResponse(FleetTaskBase):
    """Response schema for fleet task."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Maintenance Log Schemas ==============
class MaintenanceLogBase(BaseModel):
    """Base maintenance log schema."""
    vehicle_id: int
    issue_type: str
    severity: Optional[str] = "medium"
    predicted_by_ai: Optional[bool] = False
    status: Optional[str] = "pending"


class MaintenanceLogCreate(MaintenanceLogBase):
    """Schema for creating maintenance log."""
    pass


class MaintenanceLogResponse(MaintenanceLogBase):
    """Response schema for maintenance log."""
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== Fleet Owner/Auth Schemas ==============
class FleetOwnerBase(BaseModel):
    """Base fleet owner schema."""
    name: str
    email: EmailStr
    role: Optional[str] = "owner"


class FleetOwnerCreate(FleetOwnerBase):
    """Schema for creating fleet owner (registration)."""
    password: str


class FleetOwnerResponse(FleetOwnerBase):
    """Response schema for fleet owner."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"
    user: FleetOwnerResponse


# ============== Sensor Ingestion Response ==============
class SensorIngestionResponse(BaseModel):
    """Response after sensor data ingestion with ML predictions."""
    sensor_data_id: int
    prediction_id: int
    vehicle_id: int
    failure: int
    confidence: float
    anomaly: bool
    iso_score: float
    message: str
    timestamp: datetime
