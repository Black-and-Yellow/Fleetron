"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FleetOwner
from app.schemas import FleetOwnerCreate, FleetOwnerResponse, LoginRequest, LoginResponse
import hashlib

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


@router.post("/register", response_model=FleetOwnerResponse, status_code=status.HTTP_201_CREATED)
def register(user: FleetOwnerCreate, db: Session = Depends(get_db)):
    """Register a new fleet owner/operator."""
    # Check if email already exists
    existing = db.query(FleetOwner).filter(FleetOwner.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = FleetOwner(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    # Find user
    user = db.query(FleetOwner).filter(FleetOwner.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate simple token (in production, use JWT)
    token = hashlib.sha256(f"{user.email}:{user.id}".encode()).hexdigest()
    
    # Build response
    user_response = FleetOwnerResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at
    )
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )
