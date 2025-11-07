"""Fleet tasks router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import FleetTask
from app.schemas import FleetTaskCreate, FleetTaskResponse
from app.services.sensor_processing import verify_vehicle_exists

router = APIRouter(prefix="/tasks", tags=["Fleet Tasks"])


@router.post("/", response_model=FleetTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: FleetTaskCreate, db: Session = Depends(get_db)):
    """Create a new task for a vehicle."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, task.vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {task.vehicle_id} not found"
        )
    
    # Create task
    db_task = FleetTask(
        vehicle_id=task.vehicle_id,
        task_type=task.task_type,
        pickup_location=task.pickup_location,
        drop_location=task.drop_location,
        status=task.status,
        eta=task.eta
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.get("/{vehicle_id}", response_model=List[FleetTaskResponse])
def get_vehicle_tasks(vehicle_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific vehicle."""
    # Verify vehicle exists
    if not verify_vehicle_exists(db, vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    # Get tasks
    tasks = db.query(FleetTask).filter(FleetTask.vehicle_id == vehicle_id).all()
    
    return tasks
