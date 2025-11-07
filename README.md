# Fleet Management System - Complete End-to-End Solution

A comprehensive **Fleet Management System** with **FastAPI backend**, **PostgreSQL database**, **React frontend**, **real-time WebSocket updates**, **ML predictions**, and **Docker deployment**.

---

## 🚀 Features

### Backend (FastAPI)
- ✅ **PostgreSQL Database** with connection pooling
- ✅ **Real-time WebSocket** broadcasting for sensor updates
- ✅ **REST API** for vehicles, sensors, tasks, and maintenance
- ✅ **ML Model Integration** for predictive maintenance
- ✅ **SQLAlchemy ORM** with async support
- ✅ **Docker-ready** with docker-compose

### Frontend (React)
- ✅ **Real-time Dashboard** with vehicle cards and statistics
- ✅ **Interactive Map View** with Leaflet.js showing vehicle locations
- ✅ **Vehicle Details** with sensor history charts (Recharts)
- ✅ **Tasks Management** for fleet operations
- ✅ **Maintenance Logs** tracking with severity levels
- ✅ **Analytics Dashboard** with charts and KPIs
- ✅ **WebSocket Integration** for live updates
- ✅ **React Query** for efficient data fetching
- ✅ **TailwindCSS** for modern UI styling
- ✅ **React Router** for navigation
- ✅ **Authentication** with login/register

---

## 📁 Project Structure

```
Problem_Statement_6_fastapi/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py          # WebSocket + FastAPI app
│   │   ├── database.py      # PostgreSQL config
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── routers/         # API routes
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API layer (axios)
│   │   ├── hooks/           # Custom hooks (WebSocket)
│   │   ├── App.jsx          # Main app with routing
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── vite.config.js       # Vite config with proxy
│   ├── tailwind.config.js
│   └── postcss.config.js
├── models/                   # ML models
├── docker-compose.yml        # Docker services
└── README.md
```

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **PostgreSQL 15** (or use Docker)

### 1. Backend Setup

#### A. Using Docker (Recommended)

```bash
# Start PostgreSQL, PgAdmin, and Backend
docker-compose up -d

# The backend will be available at http://localhost:8000
# PgAdmin will be at http://localhost:5050
```

#### B. Manual Setup (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your PostgreSQL credentials:
# DATABASE_URL=postgresql+psycopg2://fleetuser:fleetpassword@localhost:5432/fleetdb

# Run migrations (create tables)
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(engine)"

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`  
**API Docs (Swagger):** `http://localhost:8000/docs`  
**WebSocket Endpoint:** `ws://localhost:8000/ws/vehicles`

---

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

---

## 🐳 Docker Deployment

The project includes a complete Docker setup:

### Services
1. **postgres** - PostgreSQL 15 database
2. **pgadmin** - Database management UI
3. **backend** - FastAPI application

### Environment Variables

Create `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql+psycopg2://fleetuser:fleetpassword@postgres:5432/fleetdb
POSTGRES_USER=fleetuser
POSTGRES_PASSWORD=fleetpassword
POSTGRES_DB=fleetdb

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@fleet.com
PGADMIN_DEFAULT_PASSWORD=admin
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# Access PostgreSQL
docker exec -it fleet-postgres psql -U fleetuser -d fleetdb
```

---

## 📡 API Endpoints

### Vehicles
- `GET /vehicles` - Get all vehicles
- `GET /vehicles/{id}` - Get vehicle by ID
- `POST /vehicles` - Create new vehicle
- `PUT /vehicles/{id}` - Update vehicle
- `DELETE /vehicles/{id}` - Delete vehicle
- `GET /vehicles/{id}/latest-sensor` - Get latest sensor data
- `GET /vehicles/{id}/predictions/latest` - Get latest predictions

### Sensor Data
- `POST /sensor-data` - Ingest sensor data (triggers WebSocket broadcast)

### Tasks
- `POST /tasks` - Create task
- `GET /tasks/{vehicle_id}` - Get tasks for vehicle

### Maintenance
- `POST /maintenance` - Create maintenance log
- `GET /maintenance/{vehicle_id}` - Get maintenance logs

### WebSocket
- `WS /ws/vehicles` - Real-time vehicle updates

---

## 🌐 Frontend Pages

### 1. **Dashboard** (`/dashboard`)
- Vehicle cards with real-time metrics
- Fleet statistics (Total, Active, Idle, Maintenance)
- WebSocket updates for sensor data
- Battery, fuel, speed, location display

### 2. **Map View** (`/map`)
- Interactive Leaflet map with vehicle markers
- Color-coded markers based on status
- Popup with vehicle details
- Status legend
- Real-time location updates

### 3. **Vehicle Details** (`/vehicles/:id`)
- Detailed vehicle information
- Real-time sensor metrics
- Sensor history charts (Recharts)
- AI predictions (maintenance, range, next service)
- Battery, fuel, speed trends

### 4. **Tasks** (`/tasks`)
- Task management interface
- Status tracking (Pending, In Progress, Completed)
- Priority levels (High, Medium, Low)
- Task assignment to vehicles
- Due date tracking

### 5. **Maintenance** (`/maintenance`)
- Maintenance log tracking
- Severity levels (High, Medium, Low)
- Status workflow (Pending → In Progress → Resolved)
- Issue descriptions and notes
- Resolution tracking

### 6. **Analytics** (`/analytics`)
- Fleet utilization trends
- Maintenance cost analysis
- Fuel efficiency metrics
- Distance traveled statistics
- Interactive charts and KPIs

### 7. **Login/Register** (`/login`)
- User authentication
- Login and registration forms
- Token-based auth with localStorage

---

## 🔌 WebSocket Integration

### Backend (ConnectionManager)
```python
# In app/main.py
manager = ConnectionManager()

@app.websocket("/ws/vehicles")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Broadcasts sensor updates to all clients
```

### Frontend (useWebSocket Hook)
```javascript
// In src/hooks/useWebSocket.js
const { messages, sendMessage } = useWebSocket('ws://localhost:8000/ws/vehicles');

// Automatically reconnects on disconnect
// Updates state when new sensor data arrives
```

---

## 🎨 Frontend Tech Stack

| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite 7** | Build tool & dev server |
| **TailwindCSS 3** | Utility-first CSS |
| **React Router 6** | Client-side routing |
| **React Query** | Data fetching & caching |
| **Axios** | HTTP client |
| **Leaflet.js** | Map visualization |
| **Recharts** | Data visualization |
| **Lucide React** | Icon library |
| **WebSocket API** | Real-time updates |

---

## 🔐 Authentication

The frontend includes authentication with:
- Login/Register pages
- JWT token storage in localStorage
- Protected routes with authentication guard
- Token injection in API requests via Axios interceptor

---

## 📊 Real-time Updates

The system uses WebSockets for real-time communication:

1. **Sensor Ingestion** → Backend receives sensor data
2. **Broadcast** → Backend broadcasts to all WebSocket clients
3. **Frontend Update** → React components update in real-time
4. **UI Refresh** → Dashboard, Map, and Vehicle Details auto-update

---

## 🧪 Testing the System

### 1. Start Backend & Database
```bash
docker-compose up -d
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test WebSocket Updates
```bash
# Send sensor data to trigger WebSocket broadcast
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "speed": 65.5,
    "fuel_level": 75.0,
    "battery_level": 88.0
  }'
```

### 4. Access Services
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PgAdmin:** http://localhost:5050

---

## 🐛 Troubleshooting

### Backend Issues

**PostgreSQL Connection Error:**
```bash
# Check if PostgreSQL is running
docker ps

# Check logs
docker-compose logs postgres

# Restart services
docker-compose restart postgres backend
```

**WebSocket Not Connecting:**
- Check if backend is running on port 8000
- Verify WebSocket URL in frontend: `ws://localhost:8000/ws/vehicles`
- Check browser console for WebSocket errors

### Frontend Issues

**Module Not Found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Map Not Displaying:**
- Ensure Leaflet CSS is imported
- Check network tab for tile loading errors
- Verify vehicle data has latitude/longitude

**WebSocket Reconnection Loop:**
- Check backend logs for errors
- Verify WebSocket endpoint is accessible
- Ensure backend is running before frontend connects

---

## 📈 Production Deployment

### Backend
1. Use environment variables for sensitive data
2. Enable CORS only for specific origins
3. Use production-grade PostgreSQL instance
4. Set up SSL/TLS for WebSocket connections
5. Use reverse proxy (Nginx) for load balancing

### Frontend
```bash
cd frontend
npm run build
# Deploy 'dist' folder to hosting service (Vercel, Netlify, etc.)
```

### Environment Variables for Production
```env
VITE_API_URL=https://your-backend-api.com
VITE_WS_URL=wss://your-backend-api.com/ws/vehicles
```

---

## 📝 API Documentation

Full API documentation is available at: `http://localhost:8000/docs` (Swagger UI)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **PostgreSQL** - Robust database
- **Leaflet.js** - Open-source mapping library
- **TailwindCSS** - Utility-first CSS framework

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at `/docs`
- Review Docker logs: `docker-compose logs -f`

---

**Built with ❤️ using FastAPI, React, PostgreSQL, and WebSockets**
