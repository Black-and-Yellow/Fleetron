from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_name = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=False)
    status = Column(String, default="active")  # active, inactive, maintenance
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor_data = relationship("SensorData", back_populates="vehicle", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="vehicle", cascade="all, delete-orphan")
    tasks = relationship("FleetTask", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle", cascade="all, delete-orphan")


class SensorData(Base):
    """Sensor data collected from vehicles in real-time."""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    gps_lat = Column(Float)
    gps_lon = Column(Float)
    speed = Column(Float)
    battery = Column(Float)
    acc_x = Column(Float)
    acc_y = Column(Float)
    acc_z = Column(Float)
    temp_motor = Column(Float)
    raw_payload = Column(JSON)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="sensor_data")


class Prediction(Base):
    """ML prediction results for vehicle health and anomalies."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    failure_prediction = Column(Integer)  # 0 or 1
    failure_confidence = Column(Float)
    anomaly_flag = Column(Integer)  # 0 or 1
    iso_score = Column(Float)
    message = Column(String)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="predictions")


class FleetTask(Base):
    """Tasks assigned to vehicles (pickup/delivery routes)."""
    __tablename__ = "fleet_tasks"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    task_type = Column(String)  # delivery, pickup, patrol, etc.
    pickup_location = Column(JSON)  # {"lat": x, "lon": y, "address": "..."}
    drop_location = Column(JSON)
    status = Column(String, default="assigned")  # assigned, ongoing, completed
    eta = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="tasks")


class MaintenanceLog(Base):
    """Maintenance logs for vehicles, including AI-predicted issues."""
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    issue_type = Column(String, nullable=False)  # motor_failure, battery_issue, etc.
    severity = Column(String, default="medium")  # low, medium, high, critical
    predicted_by_ai = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending, in_progress, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="maintenance_logs")


class FleetOwner(Base):
    """Fleet owner/operator user accounts."""
    __tablename__ = "fleet_owners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="owner")  # admin, owner, operator
    created_at = Column(DateTime, default=datetime.utcnow)
