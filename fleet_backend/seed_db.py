"""
Database Seeding Script for Fleet Management System
====================================================

This script populates the database with sample data:
- Fleet vehicles
- Sensor data readings
- Predictions (failure/anomaly)
- Fleet tasks
- Maintenance logs
- Fleet owner accounts
"""

import sys
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
import hashlib

# Add app to path
sys.path.append('.')

from app.database import SessionLocal, init_db
from app.models import Vehicle, SensorData, Prediction, FleetTask, MaintenanceLog, FleetOwner


def get_hash_password(password: str) -> str:
    """Hash a password using SHA256 (for demo purposes)."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_fleet_owners(db: Session):
    """Create sample fleet owner accounts."""
    print("\n📋 Seeding Fleet Owners...")
    
    owners = [
        {
            "name": "Admin User",
            "email": "admin@nexsync.com",
            "password_hash": get_hash_password("admin123"),
            "role": "admin"
        },
        {
            "name": "Fleet Manager",
            "email": "manager@nexsync.com",
            "password_hash": get_hash_password("manager123"),
            "role": "owner"
        },
        {
            "name": "Fleet Operator",
            "email": "operator@nexsync.com",
            "password_hash": get_hash_password("operator123"),
            "role": "operator"
        }
    ]
    
    for owner_data in owners:
        # Check if already exists
        existing = db.query(FleetOwner).filter(FleetOwner.email == owner_data["email"]).first()
        if not existing:
            owner = FleetOwner(**owner_data)
            db.add(owner)
            print(f"  ✓ Created: {owner_data['email']} (password: {owner_data['email'].split('@')[0].replace('admin', 'admin123').replace('manager', 'manager123').replace('operator', 'operator123')})")
    
    db.commit()
    print(f"  ✓ {len(owners)} fleet owners seeded")


def seed_vehicles(db: Session, count: int = 10):
    """Create sample vehicles."""
    print(f"\n🚗 Seeding {count} Vehicles...")
    
    models = [
        "NexSync-AutoX1", "NexSync-AutoX2", "NexSync-CargoV3",
        "NexSync-DeliveryBot", "NexSync-PatrolUnit", "NexSync-Shuttle"
    ]
    
    statuses = ["active", "active", "active", "active", "inactive", "maintenance"]
    
    vehicles = []
    for i in range(1, count + 1):
        # Check if already exists
        existing = db.query(Vehicle).filter(Vehicle.vehicle_name == f"vehicle-{i}").first()
        if existing:
            vehicles.append(existing)
            print(f"  ℹ Vehicle vehicle-{i} already exists (id={existing.id})")
            continue
        
        vehicle = Vehicle(
            vehicle_name=f"vehicle-{i}",
            model=random.choice(models),
            status=random.choice(statuses),
            last_seen=datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
        )
        db.add(vehicle)
        vehicles.append(vehicle)
    
    db.commit()
    
    # Refresh to get IDs
    for vehicle in vehicles:
        db.refresh(vehicle)
    
    print(f"  ✓ {len([v for v in vehicles if v.id])} vehicles seeded")
    return vehicles


def seed_sensor_data(db: Session, vehicles: list, readings_per_vehicle: int = 50):
    """Create sample sensor data for vehicles."""
    print(f"\n📡 Seeding Sensor Data ({readings_per_vehicle} readings per vehicle)...")
    
    total_count = 0
    
    for vehicle in vehicles:
        # Generate sensor readings over the past 24 hours
        base_time = datetime.utcnow() - timedelta(hours=24)
        time_increment = timedelta(hours=24) / readings_per_vehicle
        
        # Starting position (San Francisco area)
        base_lat = 37.7749 + random.uniform(-0.1, 0.1)
        base_lon = -122.4194 + random.uniform(-0.1, 0.1)
        
        for i in range(readings_per_vehicle):
            timestamp = base_time + (time_increment * i)
            
            # Simulate vehicle movement
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            
            # Normal operating conditions with occasional anomalies
            is_anomaly = random.random() < 0.05  # 5% anomaly rate
            
            sensor = SensorData(
                vehicle_id=vehicle.id,
                timestamp=timestamp,
                gps_lat=base_lat + lat_offset,
                gps_lon=base_lon + lon_offset,
                speed=round(random.uniform(0, 80) if not is_anomaly else random.uniform(85, 120), 2),
                battery=round(random.uniform(20, 100) if not is_anomaly else random.uniform(5, 15), 2),
                acc_x=round(random.uniform(-2, 2) if not is_anomaly else random.uniform(-5, 5), 3),
                acc_y=round(random.uniform(-2, 2) if not is_anomaly else random.uniform(-5, 5), 3),
                acc_z=round(random.uniform(-2, 2) if not is_anomaly else random.uniform(-5, 5), 3),
                temp_motor=round(random.uniform(30, 85) if not is_anomaly else random.uniform(95, 120), 2),
                raw_payload={
                    "sensor_version": "v2.1.0",
                    "location": random.choice(["highway_101", "downtown", "warehouse_district", "airport"]),
                    "weather": random.choice(["clear", "cloudy", "rainy", "foggy"])
                }
            )
            db.add(sensor)
            total_count += 1
        
        # Commit per vehicle to avoid large transactions
        db.commit()
        print(f"  ✓ Vehicle {vehicle.vehicle_name}: {readings_per_vehicle} readings")
    
    print(f"  ✓ Total: {total_count} sensor readings seeded")


def seed_predictions(db: Session, vehicles: list):
    """Create sample predictions based on sensor data."""
    print(f"\n🤖 Seeding Predictions...")
    
    total_count = 0
    
    for vehicle in vehicles:
        # Get all sensor data for this vehicle
        sensor_data = db.query(SensorData).filter(
            SensorData.vehicle_id == vehicle.id
        ).all()
        
        for sensor in sensor_data:
            # Determine if this is a failure/anomaly case
            is_high_temp = sensor.temp_motor > 90
            is_low_battery = sensor.battery < 20
            is_high_speed = sensor.speed > 80
            
            # Calculate failure prediction
            failure_prediction = 1 if (is_high_temp or is_low_battery) else 0
            failure_confidence = random.uniform(0.7, 0.95) if failure_prediction == 1 else random.uniform(0.05, 0.3)
            
            # Calculate anomaly detection
            anomaly_flag = 1 if (is_high_temp or is_low_battery or is_high_speed) else 0
            iso_score = random.uniform(-0.5, -0.1) if anomaly_flag == 1 else random.uniform(0.1, 0.5)
            
            # Generate message
            if failure_prediction == 1 and is_high_temp:
                message = f"⚠️ High motor temperature detected ({sensor.temp_motor}°C). Failure risk: HIGH"
            elif failure_prediction == 1 and is_low_battery:
                message = f"⚠️ Low battery level ({sensor.battery}%). Failure risk: HIGH"
            elif anomaly_flag == 1:
                message = "⚠️ Anomalous behavior detected. System flagged for review"
            else:
                message = "✓ All systems normal"
            
            prediction = Prediction(
                vehicle_id=vehicle.id,
                timestamp=sensor.timestamp,
                failure_prediction=failure_prediction,
                failure_confidence=failure_confidence,
                anomaly_flag=anomaly_flag,
                iso_score=iso_score,
                message=message
            )
            db.add(prediction)
            total_count += 1
        
        db.commit()
        print(f"  ✓ Vehicle {vehicle.vehicle_name}: {len(sensor_data)} predictions")
    
    print(f"  ✓ Total: {total_count} predictions seeded")


def seed_fleet_tasks(db: Session, vehicles: list, tasks_per_vehicle: int = 5):
    """Create sample fleet tasks."""
    print(f"\n📦 Seeding Fleet Tasks ({tasks_per_vehicle} tasks per vehicle)...")
    
    task_types = ["delivery", "pickup", "patrol", "maintenance_check", "inspection"]
    statuses = ["assigned", "ongoing", "completed"]
    
    locations = [
        {"lat": 37.7749, "lon": -122.4194, "address": "123 Market St, San Francisco, CA"},
        {"lat": 37.8044, "lon": -122.2712, "address": "456 Broadway, Oakland, CA"},
        {"lat": 37.3382, "lon": -121.8863, "address": "789 First St, San Jose, CA"},
        {"lat": 37.6879, "lon": -122.4702, "address": "321 Airport Blvd, San Francisco, CA"},
        {"lat": 37.8716, "lon": -122.2727, "address": "654 University Ave, Berkeley, CA"}
    ]
    
    total_count = 0
    
    for vehicle in vehicles:
        for i in range(tasks_per_vehicle):
            pickup_loc = random.choice(locations)
            drop_loc = random.choice([loc for loc in locations if loc != pickup_loc])
            
            created_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            eta_hours = random.randint(1, 6)
            
            task = FleetTask(
                vehicle_id=vehicle.id,
                task_type=random.choice(task_types),
                pickup_location=pickup_loc,
                drop_location=drop_loc,
                status=random.choice(statuses),
                eta=created_time + timedelta(hours=eta_hours),
                created_at=created_time
            )
            db.add(task)
            total_count += 1
        
        db.commit()
        print(f"  ✓ Vehicle {vehicle.vehicle_name}: {tasks_per_vehicle} tasks")
    
    print(f"  ✓ Total: {total_count} tasks seeded")


def seed_maintenance_logs(db: Session, vehicles: list):
    """Create sample maintenance logs."""
    print(f"\n🔧 Seeding Maintenance Logs...")
    
    issue_types = [
        "motor_failure", "battery_issue", "sensor_malfunction",
        "tire_wear", "brake_check", "software_update",
        "camera_calibration", "lidar_alignment"
    ]
    
    severities = ["low", "medium", "high", "critical"]
    statuses = ["pending", "in_progress", "resolved"]
    
    total_count = 0
    
    for vehicle in vehicles:
        # Get predictions with failures for this vehicle
        failure_predictions = db.query(Prediction).filter(
            Prediction.vehicle_id == vehicle.id,
            Prediction.failure_prediction == 1
        ).limit(3).all()
        
        # Create maintenance logs for predicted failures
        for pred in failure_predictions:
            log = MaintenanceLog(
                vehicle_id=vehicle.id,
                issue_type=random.choice(issue_types),
                severity=random.choice(["high", "critical"]),
                predicted_by_ai=True,
                status=random.choice(statuses),
                created_at=pred.timestamp,
                resolved_at=pred.timestamp + timedelta(hours=random.randint(2, 48)) if random.random() > 0.3 else None
            )
            db.add(log)
            total_count += 1
        
        # Add some routine maintenance logs
        for _ in range(random.randint(1, 3)):
            created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            is_resolved = random.random() > 0.4
            
            log = MaintenanceLog(
                vehicle_id=vehicle.id,
                issue_type=random.choice(issue_types),
                severity=random.choice(severities),
                predicted_by_ai=False,
                status="resolved" if is_resolved else random.choice(["pending", "in_progress"]),
                created_at=created_time,
                resolved_at=created_time + timedelta(hours=random.randint(2, 72)) if is_resolved else None
            )
            db.add(log)
            total_count += 1
        
        db.commit()
        print(f"  ✓ Vehicle {vehicle.vehicle_name}: {len(failure_predictions) + random.randint(1, 3)} logs")
    
    print(f"  ✓ Total: {total_count} maintenance logs seeded")


def clear_database(db: Session):
    """Clear all data from database (optional)."""
    print("\n🗑️  Clearing existing data...")
    
    db.query(MaintenanceLog).delete()
    db.query(FleetTask).delete()
    db.query(Prediction).delete()
    db.query(SensorData).delete()
    db.query(Vehicle).delete()
    db.query(FleetOwner).delete()
    
    db.commit()
    print("  ✓ Database cleared")


def main():
    """Main seeding function."""
    print("=" * 70)
    print("  FLEET MANAGEMENT SYSTEM - DATABASE SEEDING")
    print("=" * 70)
    
    # Initialize database (create tables if not exist)
    print("\n📊 Initializing database...")
    init_db()
    print("  ✓ Database tables ready")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Ask user if they want to clear existing data
        response = input("\n⚠️  Clear existing data? (y/N): ").strip().lower()
        if response == 'y':
            clear_database(db)
        
        # Seed data
        seed_fleet_owners(db)
        vehicles = seed_vehicles(db, count=10)
        seed_sensor_data(db, vehicles, readings_per_vehicle=50)
        seed_predictions(db, vehicles)
        seed_fleet_tasks(db, vehicles, tasks_per_vehicle=5)
        seed_maintenance_logs(db, vehicles)
        
        print("\n" + "=" * 70)
        print("  ✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        # Summary
        vehicle_count = db.query(Vehicle).count()
        sensor_count = db.query(SensorData).count()
        prediction_count = db.query(Prediction).count()
        task_count = db.query(FleetTask).count()
        maintenance_count = db.query(MaintenanceLog).count()
        owner_count = db.query(FleetOwner).count()
        
        print("\n📈 Database Summary:")
        print(f"  • Fleet Owners: {owner_count}")
        print(f"  • Vehicles: {vehicle_count}")
        print(f"  • Sensor Readings: {sensor_count}")
        print(f"  • Predictions: {prediction_count}")
        print(f"  • Fleet Tasks: {task_count}")
        print(f"  • Maintenance Logs: {maintenance_count}")
        
        print("\n🔐 Login Credentials:")
        print("  • admin@nexsync.com / admin123")
        print("  • manager@nexsync.com / manager123")
        print("  • operator@nexsync.com / operator123")
        
        print("\n🚀 Next Steps:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Open API docs: http://localhost:8000/docs")
        print("  3. Test endpoints: GET /vehicles, GET /sensor-data, etc.")
        print("  4. Start frontend: cd ../frontend && npm run dev")
        
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
