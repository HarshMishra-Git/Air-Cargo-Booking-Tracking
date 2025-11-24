# High Level Design (HLD)
## Air Cargo Booking & Tracking System

---

## 1. SYSTEM OVERVIEW

The Air Cargo Booking & Tracking System is a full-stack web application designed to handle air cargo bookings and track shipments through their journey. The system supports high throughput (50K bookings/day, 150K updates/day) with real-time tracking capabilities.

### Key Features
- Create bookings with auto-generated reference IDs (format: ACB12345)
- Search direct and transit flight routes (1-hop maximum)
- Update booking status (BOOKED → DEPARTED → ARRIVED → DELIVERED)
- Track booking history with chronological timeline
- Cancel bookings (not allowed after arrival)
- List bookings with pagination
- JWT-based authentication
- Handle concurrent updates using distributed locks
- Cache frequently accessed data for performance
- Rate limiting (60 requests/minute per IP)

---

## 2. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Next.js Frontend (React + TypeScript)             │   │
│  │                                                            │   │
│  │  • Booking Creation Form                                  │   │
│  │  • Route Search Interface                                 │   │
│  │  • Booking Tracking Dashboard                             │   │
│  │  • Timeline Visualization                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Python)                     │   │
│  │                                                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │   Booking  │  │   Route    │  │  Tracking  │         │   │
│  │  │   Service  │  │  Service   │  │  Service   │         │   │
│  │  └────────────┘  └────────────┘  └────────────┘         │   │
│  │                                                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │  Booking   │  │   Flight   │  │   Event    │         │   │
│  │  │ Repository │  │ Repository │  │ Repository │         │   │
│  │  └────────────┘  └────────────┘  └────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    CACHE LAYER           │    │    LOCK LAYER            │
│  ┌────────────────────┐  │    │  ┌────────────────────┐  │
│  │      Redis         │  │    │  │      Redis         │  │
│  │   (Cache Store)    │  │    │  │  (Distributed      │  │
│  │                    │  │    │  │      Locks)        │  │
│  │  • Route Cache     │  │    │  │                    │  │
│  │  • Booking Cache   │  │    │  │  • Redlock Algo    │  │
│  │  • TTL Management  │  │    │  │  • Concurrency     │  │
│  └────────────────────┘  │    │  │    Control         │  │
└──────────────────────────┘    │  └────────────────────┘  │
                                └──────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  PostgreSQL Database                      │   │
│  │                                                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │  bookings  │  │   flights  │  │  booking_  │         │   │
│  │  │   table    │  │   table    │  │   events   │         │   │
│  │  └────────────┘  └────────────┘  └────────────┘         │   │
│  │                                                            │   │
│  │  • B-Tree Indexes on ref_id, status, routes              │   │
│  │  • Composite Indexes for route search                     │   │
│  │  • Foreign Key Constraints                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPONENT ARCHITECTURE

### 3.1 Backend Components

#### API Layer (Routers)
- **bookings.py**: Handles booking CRUD operations
- **routes.py**: Handles route search
- **health.py**: Health check endpoints

#### Service Layer
- **BookingService**: Business logic for bookings
- **RouteService**: Route search with caching
- **TrackingService**: Booking history retrieval

#### Repository Layer
- **BookingRepository**: Database operations for bookings
- **FlightRepository**: Flight queries and route finding
- **EventRepository**: Event timeline management

#### Core Components
- **Database (db.py)**: SQLAlchemy async session management
- **Cache (cache.py)**: Redis caching service
- **Locks (locks.py)**: Distributed locking with Redlock
- **Config (config.py)**: Centralized configuration
- **Logging (logging.py)**: Structured logging

---

## 4. DATABASE DESIGN

### 4.1 Schema

#### Bookings Table
```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    ref_id VARCHAR(20) UNIQUE NOT NULL,
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    pieces INTEGER NOT NULL,
    weight_kg INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'BOOKED',
    flight_ids INTEGER[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Flights Table
```sql
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    airline_name VARCHAR(100) NOT NULL,
    departure_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    arrival_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Booking Events Table
```sql
CREATE TABLE booking_events (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    event_type VARCHAR(20) NOT NULL,
    location VARCHAR(10),
    flight_id INTEGER REFERENCES flights(id),
    flight_number VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Indexes

**Performance-Critical Indexes:**
- `idx_bookings_ref_id` - Unique index on ref_id for fast lookup
- `idx_bookings_status` - Index on status for filtering
- `idx_bookings_created_at` - Descending index for recent bookings
- `idx_flights_route_date` - Composite index (origin, destination, departure_datetime)
- `idx_flights_origin` - Index on origin for route search
- `idx_flights_destination` - Index on destination for route search
- `idx_booking_events_booking_id` - Composite index (booking_id, created_at)

**Query Optimization:**
- Route search uses composite index to find flights efficiently
- Booking lookup by ref_id uses unique index (O(log n))
- Event timeline retrieval uses composite index for sorted results

---

## 5. CACHING STRATEGY

### 5.1 Cache Keys

| Resource | Key Pattern | TTL | Reason |
|----------|-------------|-----|--------|
| Routes | `route:{origin}:{dest}:{date}` | 3600s (1 hour) | Flight schedules change infrequently |
| Booking | `booking:{ref_id}` | 300s (5 min) | Balance between freshness and performance |
| Booking History | `booking_history:{ref_id}` | 300s (5 min) | Timeline updates less frequently than status |

### 5.2 Cache Invalidation

**Explicit Invalidation:**
- On booking status update → Delete `booking:{ref_id}` and `booking_history:{ref_id}`
- On booking cancellation → Delete cached booking data
- Pattern-based deletion for related keys

**TTL-Based Expiration:**
- All cached data has TTL to prevent stale data
- Routes cached longer due to infrequent changes
- Booking data has shorter TTL for near real-time updates

---

## 6. DISTRIBUTED LOCKING

### 6.1 Redlock Algorithm

**Implementation:**
- Redis-based distributed lock
- Lock key format: `lock:{resource_type}:{resource_id}`
- Lock timeout: 10 seconds (configurable)
- Retry strategy: 50 attempts with 100ms delay

**Use Cases:**
- Booking status updates (prevent race conditions)
- Concurrent depart/arrive operations
- Cancellation requests

### 6.2 Lock Flow

```
1. Client requests booking update
2. Acquire lock: SET lock:booking:ACB12345 {uuid} NX EX 10
3. If lock acquired:
   - Validate current state
   - Update database
   - Create event
   - Invalidate cache
   - Release lock
4. If lock not acquired:
   - Retry with exponential backoff
   - Return 409 Conflict after max retries
```

---

## 7. ROUTE SEARCH ALGORITHM

### 7.1 Direct Flight Search

```python
1. Query flights table:
   WHERE origin = {origin}
     AND destination = {destination}
     AND departure_datetime BETWEEN {start_of_day} AND {end_of_day}
   ORDER BY departure_datetime
```

### 7.2 Transit Route Search

```python
1. Find first leg flights:
   - Origin = {origin}
   - Departure date = {requested_date}

2. For each first leg flight:
   a. Transit airport = first_leg.destination
   b. Minimum connection time = 2 hours
   c. Earliest departure = first_leg.arrival + 2 hours
   d. Latest departure = end of next day
   
   e. Find second leg flights:
      - Origin = transit_airport
      - Destination = {destination}
      - Departure BETWEEN earliest_departure AND latest_departure
   
   f. Combine as transit route

3. Return all valid transit routes
```

**Constraints:**
- Second hop must be same day or next day only
- Minimum connection time: 2 hours
- Maximum 1 stop (one-hop transit)

---

## 8. CONCURRENCY HANDLING

### 8.1 Problem Statement

With 150K updates per day, multiple users may update the same booking simultaneously:
- User A: Marks booking as DEPARTED
- User B: Cancels the same booking
- Without locking: Race condition, inconsistent state

### 8.2 Solution

**Distributed Locks with Redlock:**
1. Each state-changing operation acquires a lock
2. Lock is resource-specific (per booking)
3. Operations are serialized at the booking level
4. Lock auto-expires to prevent deadlocks

**Validation:**
- After acquiring lock, validate current state
- Enforce state transition rules
- Prevent invalid operations (e.g., cancel after arrival)

---

## 9. SCALABILITY CONSIDERATIONS

### 9.1 Current Load

- **New Bookings**: 50K/day ≈ 0.6 bookings/sec
- **Updates**: 150K/day ≈ 1.7 updates/sec
- **Peak Load**: Assume 10x during peak hours ≈ 17 ops/sec

### 9.2 Scaling Strategy

**Horizontal Scaling:**
- Stateless FastAPI instances (can scale to N replicas)
- Load balancer distributes requests
- Shared Redis for cache and locks
- PostgreSQL read replicas for read-heavy workloads

**Database Optimization:**
- Connection pooling (20 connections per instance)
- Prepared statements
- Query result caching
- Partitioning bookings table by date (future)

**Caching:**
- Cache hit rate target: >80%
- Reduces database load significantly
- Redis cluster for high availability

**Async Processing:**
- FastAPI async handlers (non-blocking I/O)
- AsyncPG for database (async driver)
- Redis async client

---

## 10. MONITORING & OBSERVABILITY

### 10.1 Logging Strategy

**Structured Logging:**
- Request/Response logging with duration
- Unique request ID per request
- Error logging with stack traces
- Business event logging (booking created, status changed)

**Log Levels:**
- DEBUG: Cache hits/misses, lock acquisition
- INFO: API requests, business operations
- WARNING: Retry attempts, degraded performance
- ERROR: Operation failures, exceptions

### 10.2 Metrics (Optional - Prometheus)

**Application Metrics:**
- Request rate, latency, error rate
- Booking creation rate
- Cache hit/miss ratio
- Lock acquisition time

**Infrastructure Metrics:**
- Database connection pool usage
- Redis memory usage
- API response times

---

## 11. API DESIGN

### 11.1 REST Endpoints

#### Bookings
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - List bookings (paginated)
- `GET /api/v1/bookings/{ref_id}` - Get booking
- `GET /api/v1/bookings/{ref_id}/history` - Get booking history
- `POST /api/v1/bookings/{ref_id}/depart` - Mark as departed
- `POST /api/v1/bookings/{ref_id}/arrive` - Mark as arrived
- `POST /api/v1/bookings/{ref_id}/deliver` - Mark as delivered
- `DELETE /api/v1/bookings/{ref_id}` - Cancel booking

#### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Routes
- `POST /api/v1/routes/search` - Search routes

#### Health
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check

### 11.2 Error Handling

**HTTP Status Codes:**
- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 404: Not Found
- 409: Conflict (concurrent update)
- 500: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message"
}
```

---

## 12. SECURITY CONSIDERATIONS

### 12.1 Current Implementation

- CORS configuration for frontend origin
- Input validation with Pydantic
- SQL injection prevention (ORM)
- Connection pooling limits

### 12.2 Production Recommendations

- Add authentication (JWT tokens)
- Rate limiting per user/IP
- API key validation
- HTTPS/TLS encryption
- Database connection encryption
- Redis password authentication

---

## 13. DEPLOYMENT ARCHITECTURE

### 13.1 Docker Compose Setup

```yaml
Services:
- postgres: PostgreSQL database
- redis: Redis cache and locks
- backend: FastAPI application
- frontend: Next.js application

Networks:
- aircargo_network: Internal network

Volumes:
- postgres_data: Persistent database storage
- redis_data: Persistent Redis storage
```

### 13.2 Production Deployment

**Recommended Stack:**
- **Container Orchestration**: Kubernetes
- **Load Balancer**: Nginx/Traefik
- **Database**: Managed PostgreSQL (AWS RDS, Azure Database)
- **Cache**: Managed Redis (AWS ElastiCache, Azure Cache)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

---

## 14. DATA FLOW DIAGRAMS

### 14.1 Create Booking Flow

```
User → Frontend → POST /api/v1/bookings
                      ↓
                  Booking Service
                      ↓
            Generate unique ref_id
                      ↓
            Create booking in DB
                      ↓
            Create BOOKED event
                      ↓
            Commit transaction
                      ↓
            Return booking ← Frontend ← User
```

### 14.2 Update Booking Status Flow

```
User → Frontend → POST /api/v1/bookings/{ref_id}/depart
                      ↓
                  Booking Service
                      ↓
            Acquire distributed lock
                      ↓
            Get booking from DB
                      ↓
            Validate state transition
                      ↓
            Update status in DB
                      ↓
            Create DEPARTED event
                      ↓
            Invalidate cache
                      ↓
            Release lock
                      ↓
            Commit transaction
                      ↓
            Return updated booking ← Frontend ← User
```

### 14.3 Route Search Flow

```
User → Frontend → POST /api/v1/routes/search
                      ↓
                  Route Service
                      ↓
            Check cache (route:DEL:BLR:2025-12-01)
                      ↓
            Cache Hit? → Return cached data
                      ↓
            Cache Miss → Query flights DB
                      ↓
            Find direct flights
                      ↓
            Find transit routes
                      ↓
            Calculate durations
                      ↓
            Cache results (TTL: 1 hour)
                      ↓
            Return routes ← Frontend ← User
```

---

## 15. FAILURE SCENARIOS & HANDLING

### 15.1 Database Connection Failure

**Scenario**: PostgreSQL is unreachable

**Handling**:
- Connection pool retry logic
- Return 500 error to client
- Log error for monitoring
- Health check reports unhealthy

### 15.2 Redis Connection Failure

**Scenario**: Redis is unreachable

**Handling**:
- Cache operations fail gracefully (return None)
- Application continues without cache
- Lock operations fail → Return 409 to client
- Health check reports degraded

### 15.3 Concurrent Update Conflict

**Scenario**: Two users update same booking

**Handling**:
- First user acquires lock
- Second user retries (50 attempts, 100ms delay)
- If lock not acquired → Return 409 Conflict
- Client can retry request

### 15.4 Lock Not Released

**Scenario**: Application crashes while holding lock

**Handling**:
- Lock has TTL (10 seconds)
- Lock auto-expires
- Next operation can acquire lock
- No permanent deadlock

---

## 16. PERFORMANCE BENCHMARKS

### 16.1 Expected Performance

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| Create Booking | < 100ms | Single DB insert + event |
| Get Booking (cached) | < 10ms | Redis lookup |
| Get Booking (uncached) | < 50ms | DB query with index |
| Update Status | < 150ms | Lock + DB update + event |
| Route Search (cached) | < 10ms | Redis lookup |
| Route Search (uncached) | < 200ms | Complex DB query |
| Get Booking History | < 100ms | Join query with index |

### 16.2 Throughput

**Single Instance:**
- Bookings: 100-200 req/sec
- Route Search: 500-1000 req/sec (with cache)
- Status Updates: 50-100 req/sec (lock overhead)

**Scaled (5 instances):**
- Bookings: 500-1000 req/sec
- Route Search: 2500-5000 req/sec
- Status Updates: 250-500 req/sec

---

## 17. FUTURE ENHANCEMENTS

### 17.1 Planned Features

1. **User Authentication**
   - JWT-based auth
   - Role-based access control
   - API key management

2. **Advanced Search**
   - Search bookings by date range
   - Filter by status
   - Search by origin/destination

3. **Notifications**
   - Email notifications on status change
   - SMS alerts
   - Webhook support

4. **Analytics Dashboard**
   - Booking volume trends
   - Route popularity
   - Average transit time

5. **Multi-stop Routes**
   - Support for 2+ stops
   - Optimize for shortest duration
   - Price comparison

### 17.2 Technical Improvements

1. **Database Partitioning**
   - Partition bookings by month
   - Improve query performance

2. **Read Replicas**
   - Separate read/write operations
   - Scale read-heavy workloads

3. **Event Sourcing**
   - Complete audit trail
   - Replay capability
   - Event-driven architecture

4. **GraphQL API**
   - Alternative to REST
   - Flexible querying
   - Reduced over-fetching

---

## 18. CONCLUSION

The Air Cargo Booking & Tracking System is designed as a production-ready, scalable solution with the following highlights:

**Strengths:**
- Clean architecture with separation of concerns
- High performance with caching and indexing
- Robust concurrency handling with distributed locks
- Comprehensive error handling and logging
- Modern tech stack (FastAPI, Next.js, PostgreSQL, Redis)

**Production Readiness:**
- Docker containerization
- Health checks
- Structured logging
- Database migrations
- Comprehensive test coverage

**Scalability:**
- Stateless application servers
- Horizontal scaling capability
- Efficient database queries
- Caching strategy

This system can handle the required load (50K bookings/day, 150K updates/day) and is designed to scale beyond these requirements.

---