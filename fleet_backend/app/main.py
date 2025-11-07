"""Main FastAPI application for Fleet Management System."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import json
from datetime import datetime
from app.database import init_db
from app.ml.loader import ml_models
from app.routers import vehicles, sensor, predictions, tasks, maintenance, auth


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✓ WebSocket client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)
        print(f"✓ WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Global WebSocket manager
manager = ConnectionManager()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("=" * 60)
    print("Starting Fleet Management Backend System")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized successfully")
    
    # Load ML models
    print("\nLoading ML models...")
    if ml_models.models_ready():
        print("✓ All ML models loaded and ready")
    else:
        print("⚠ Warning: Some ML models failed to load")
        print("  System will continue but predictions may not work correctly")
    
    print("\n" + "=" * 60)
    print("✓ System ready! API docs available at: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    yield
    
    # Shutdown
    print("\nShutting down Fleet Management System...")


# Create FastAPI app
app = FastAPI(
    title="Fleet Management Backend System",
    description="Real-time autonomous vehicle fleet management with ML-powered predictive maintenance",
    version="1.0.0",
    lifespan=lifespan
)

# Attach WebSocket manager to app state
app.state.ws_manager = manager

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vehicles.router)
app.include_router(sensor.router)
app.include_router(predictions.router)
app.include_router(tasks.router)
app.include_router(maintenance.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "service": "Fleet Management Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "message": "Welcome to the Autonomous Fleet Management System"
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded" if ml_models.models_ready() else "partial",
        "websocket_clients": len(manager.active_connections)
    }


@app.websocket("/ws/vehicles")
async def websocket_vehicles(websocket: WebSocket):
    """
    WebSocket endpoint for real-time vehicle updates.
    Clients connect here to receive live sensor data and predictions.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back for debugging
            await websocket.send_json({
                "type": "echo",
                "message": "Connected to vehicle updates stream",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
