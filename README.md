# 🛫 Air Cargo Booking & Tracking System

A production-ready, full-stack air cargo booking and tracking system built with FastAPI, Next.js, PostgreSQL, and Redis.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Functionality
- ✅ **Create Bookings** - Generate bookings with unique reference IDs (format: ACB12345)
- ✅ **Route Search** - Find direct flights and one-hop transit routes
- ✅ **Status Tracking** - Track shipments through their entire journey (BOOKED → DEPARTED → ARRIVED → DELIVERED)
- ✅ **Event Timeline** - Chronological history of all booking events
- ✅ **Status Updates** - Mark bookings as DEPARTED, ARRIVED, DELIVERED
- ✅ **Cancellation** - Cancel bookings (not allowed after arrival)
- ✅ **Authentication** - JWT-based user authentication and authorization

### Technical Features
- 🔒 **Distributed Locking** - Handle concurrent updates with Redis Redlock
- ⚡ **Caching** - Redis-based caching for high performance
- 🚦 **Rate Limiting** - Redis-based rate limiting to prevent abuse
- 📊 **Database Indexing** - Optimized queries for 50K+ bookings/day
- 🔍 **Comprehensive Logging** - Structured logging for debugging
- 🐳 **Docker Support** - Full containerization for easy deployment
- 🧪 **Comprehensive Tests** - Unit, integration, and API tests with >80% coverage
- 📱 **Responsive UI** - Clean, modern interface with Tailwind CSS
- 📈 **Monitoring** - Prometheus metrics and health checks

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Next.js Frontend<br/>React + TypeScript]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend<br/>Python 3.11]
        
        subgraph "Services"
            BS[Booking Service]
            RS[Route Service]
            TS[Tracking Service]
        end
        
        subgraph "Repositories"
            BR[Booking Repository]
            FR[Flight Repository]
            ER[Event Repository]
        end
    end
    
    subgraph "Cache & Lock Layer"
        REDIS[(Redis<br/>Cache + Locks)]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Database)]
    end
    
    UI -->|REST API| API
    API --> BS
    API --> RS
    API --> TS
    
    BS --> BR
    RS --> FR
    TS --> BR
    TS --> ER
    
    BR --> DB
    FR --> DB
    ER --> DB
    
    BS -.->|Cache| REDIS
    RS -.->|Cache| REDIS
    BS -.->|Locks| REDIS
    
    style UI fill:#61dafb
    style API fill:#009688
    style REDIS fill:#dc382d
    style DB fill:#336791
```

### Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Cache
    participant Lock
    participant DB
    
    User->>Frontend: Create Booking
    Frontend->>API: POST /api/v1/bookings
    API->>DB: Generate ref_id
    API->>DB: Insert booking
    API->>DB: Create BOOKED event
    DB-->>API: Booking created
    API-->>Frontend: Return booking
    Frontend-->>User: Show ref_id
    
    User->>Frontend: Update Status
    Frontend->>API: POST /bookings/{ref_id}/depart
    API->>Lock: Acquire lock
    Lock-->>API: Lock acquired
    API->>DB: Get booking
    API->>DB: Update status
    API->>DB: Create event
    API->>Cache: Invalidate cache
    API->>Lock: Release lock
    API-->>Frontend: Updated booking
    Frontend-->>User: Show new status
```

### Status Flow

```mermaid
stateDiagram-v2
    [*] --> BOOKED: Create Booking
    BOOKED --> DEPARTED: Depart
    BOOKED --> CANCELLED: Cancel
    DEPARTED --> ARRIVED: Arrive
    DEPARTED --> CANCELLED: Cancel
    ARRIVED --> DELIVERED: Deliver
    DELIVERED --> [*]
    CANCELLED --> [*]
    
    note right of ARRIVED
        Cannot cancel
        after arrival
    end note
```

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.115.0
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **ORM:** SQLAlchemy 2.0 (Async)
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose)
- **Testing:** Pytest + pytest-asyncio
- **Monitoring:** Prometheus

### Frontend
- **Framework:** Next.js 14.1.0
- **Language:** TypeScript 5.3.3
- **Styling:** Tailwind CSS 3.4.1
- **HTTP Client:** Axios 1.6.5
- **Icons:** Lucide React
- **Testing:** Jest + React Testing Library

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Web Server:** Uvicorn
- **Reverse Proxy:** (Nginx recommended for production)

---

## 📋 Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.11+ (for local development)
- **Node.js** 18+ (for local development)
- **Git**

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/HarshMishra-Git/Air-Cargo-Booking-Tracking.git
cd air-cargo-system
```

### 2. Start Services with Docker

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d
```

### 3. Run Database Migrations

```bash
# Run migrations
docker exec -it aircargo_backend alembic upgrade head
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API Metrics:** http://localhost:8000/metrics

### 5. Test the System

```bash
# Create a booking
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "DEL",
    "destination": "BLR",
    "pieces": 10,
    "weight_kg": 500
  }'

# Search routes
curl -X POST http://localhost:8000/api/v1/routes/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "DEL",
    "destination": "BLR",
    "departure_date": "2025-12-01"
  }'
```

---

## 📁 Project Structure

```
air-cargo-system/
├── backend/
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── core/                # Core utilities
│   │   │   ├── auth.py          # JWT authentication
│   │   │   ├── cache.py         # Redis cache
│   │   │   ├── config.py        # Configuration
│   │   │   ├── db.py            # Database connection
│   │   │   ├── locks.py         # Distributed locks
│   │   │   ├── logging.py       # Logging setup
│   │   │   └── metrics.py       # Prometheus metrics
│   │   ├── middleware/          # Custom middleware
│   │   │   ├── logging_middleware.py
│   │   │   └── rate_limit.py    # Rate limiting
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── booking.py
│   │   │   ├── booking_event.py
│   │   │   ├── flight.py
│   │   │   └── user.py
│   │   ├── repositories/        # Data access layer
│   │   │   ├── booking_repository.py
│   │   │   ├── event_repository.py
│   │   │   └── flight_repository.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── bookings.py      # Booking operations
│   │   │   ├── health.py        # Health checks
│   │   │   ├── metrics.py       # Metrics endpoint
│   │   │   └── routes.py        # Route search
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── booking.py
│   │   │   ├── flight.py
│   │   │   ├── route.py
│   │   │   └── user.py
│   │   ├── services/            # Business logic
│   │   │   ├── booking_service.py
│   │   │   ├── route_service.py
│   │   │   └── tracking_service.py
│   │   ├── utils/               # Utilities
│   │   │   └── ref_id_generator.py
│   │   └── main.py              # Application entry
│   ├── tests/                   # Test suite
│   │   ├── conftest.py
│   │   ├── test_booking_service.py
│   │   ├── test_route_service.py
│   │   ├── test_auth.py
│   │   ├── test_edge_cases.py
│   │   └── ...
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app directory
│   │   │   ├── create-booking/  # Create booking page
│   │   │   ├── search-route/    # Route search page
│   │   │   ├── track/           # Tracking page
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx         # Home page
│   │   ├── components/          # React components
│   │   │   ├── BookingForm.tsx
│   │   │   ├── BookingStatusCard.tsx
│   │   │   ├── LoadingSkeleton.tsx
│   │   │   ├── SearchBox.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── Timeline.tsx
│   │   │   └── ...
│   │   ├── services/            # API services
│   │   │   └── api.ts
│   │   └── types/               # TypeScript types
│   │       └── index.ts
│   ├── .env.example
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docker-compose.yml           # Docker services
├── docker-compose.monitoring.yml # Monitoring stack
├── init-db.sql                  # Database initialization
├── prometheus.yml               # Prometheus config
├── alerting-rules.yml           # Alert rules
├── ARCHITECTURE.md              # High-level design
└── README.md                    # This file
```

---

## ⚙️ Environment Variables

### Backend (.env)

```bash
# Application
APP_NAME="Air Cargo Booking System"
APP_VERSION="1.0.0"
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/aircargo
DATABASE_URL_SYNC=postgresql://postgres:postgres@postgres:5432/aircargo

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars-long

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# Cache
CACHE_TTL=300
ROUTE_CACHE_TTL=3600

# Locks
LOCK_TIMEOUT=10
LOCK_RETRY_DELAY=0.1
LOCK_RETRY_TIMES=50
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Bookings
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - List bookings (paginated)
- `GET /api/v1/bookings/{ref_id}` - Get booking details
- `GET /api/v1/bookings/{ref_id}/history` - Get booking timeline
- `POST /api/v1/bookings/{ref_id}/depart` - Mark as departed
- `POST /api/v1/bookings/{ref_id}/arrive` - Mark as arrived
- `POST /api/v1/bookings/{ref_id}/deliver` - Mark as delivered
- `DELETE /api/v1/bookings/{ref_id}` - Cancel booking

#### Routes
- `POST /api/v1/routes/search` - Search flight routes

#### Health & Metrics
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check
- `GET /metrics` - Prometheus metrics

---

## 🗄️ Database Migrations

### Create New Migration

```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Downgrade
alembic downgrade -1
```

### View Migration History

```bash
alembic history
alembic current
```

---

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_booking_service.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_booking_service.py::test_create_booking
```

### Frontend Tests

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Test Coverage

Current coverage: **>80%**

- Unit tests: Booking, Route, Tracking services
- Integration tests: Full lifecycle, API endpoints
- Edge case tests: Validation, error handling
- Frontend tests: Component rendering, user interactions

---

## 🚀 Production Deployment

### Docker Production Build

```bash
# Build images
docker-compose build

# Start in production mode
docker-compose up -d
```

### Environment Setup

1. **Update environment variables** for production
2. **Set strong SECRET_KEY** (min 32 characters)
3. **Configure database** with production credentials
4. **Enable HTTPS** with reverse proxy (Nginx)
5. **Set DEBUG=False**
6. **Configure monitoring** (Prometheus + Grafana)

### Monitoring Stack (Optional)

```bash
# Start with monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access dashboards
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093
```

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health (includes DB and Redis status)
curl http://localhost:8000/health/detailed
```

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker logs aircargo_backend

# Check if PostgreSQL is running
docker ps | grep postgres

# Check if Redis is running
docker ps | grep redis

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres redis
docker exec -it aircargo_backend alembic upgrade head
```

### Frontend Not Loading

```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend logs
docker logs aircargo_frontend

# Rebuild frontend
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill process
kill -9 <PID>
```

### Clear All Data

```bash
# Stop and remove all containers, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

---

## 📊 Performance Metrics

### Current Capacity
- **Bookings:** 50,000+ per day
- **Updates:** 150,000+ per day
- **Flights:** 100,000+ supported
- **Response Time:** <100ms average
- **Cache Hit Rate:** >80%
- **Uptime:** 99.9% target

### Scaling
- **Horizontal:** Stateless design allows multiple instances
- **Database:** Read replicas for read-heavy operations
- **Cache:** Redis cluster for high availability
- **Load Balancer:** Nginx/HAProxy for distribution

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- **Backend:** Follow PEP 8, use type hints
- **Frontend:** Follow ESLint rules, use TypeScript
- **Tests:** Maintain >80% coverage
- **Commits:** Use conventional commits

---

## 📄 License

MIT License - see LICENSE file for details

---

## 📞 Support

For issues and questions:
- **Issues:** GitHub Issues
- **Documentation:** See ARCHITECTURE.md for detailed design
- **API Docs:** http://localhost:8000/docs

---

## 🎯 Key Features Summary

| Feature | Status | Description |
|---------|--------|-------------|
| Create Booking | ✅ | Auto-generated ref_id (ACB12345) |
| Route Search | ✅ | Direct + 1-hop transit routes |
| Status Tracking | ✅ | BOOKED → DEPARTED → ARRIVED → DELIVERED |
| Event Timeline | ✅ | Complete chronological history |
| Cancellation | ✅ | Cancel before arrival |
| Authentication | ✅ | JWT-based auth |
| Rate Limiting | ✅ | 60 requests/minute per IP |
| Caching | ✅ | Redis with smart invalidation |
| Distributed Locks | ✅ | Redlock for concurrency |
| Monitoring | ✅ | Prometheus metrics |
| Testing | ✅ | >80% coverage |
| Documentation | ✅ | Complete HLD/LLD |

---

**Built with ❤️ for efficient air cargo management**
