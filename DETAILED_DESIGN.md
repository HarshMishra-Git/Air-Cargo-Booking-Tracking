# Low Level Design (LLD)
## Air Cargo Booking & Tracking System

---

## 1. CLASS DIAGRAMS

### 1.1 Domain Models

```
┌─────────────────────────┐
│       Booking           │
├─────────────────────────┤
│ - id: int               │
│ - ref_id: str           │
│ - origin: str           │
│ - destination: str      │
│ - pieces: int           │
│ - weight_kg: int        │
│ - status: str           │
│ - flight_ids: List[int] │
│ - created_at: datetime  │
│ - updated_at: datetime  │
├─────────────────────────┤
│ + events: List[Event]   │
└─────────────────────────┘

┌─────────────────────────┐
│       Flight            │
├─────────────────────────┤
│ - id: int               │
│ - flight_number: str    │
│ - airline_name: str     │
│ - departure_datetime    │
│ - arrival_datetime      │
│ - origin: str           │
│ - destination: str      │
│ - created_at: datetime  │
│ - updated_at: datetime  │
└─────────────────────────┘

┌─────────────────────────┐
│    BookingEvent         │
├─────────────────────────┤
│ - id: int               │
│ - booking_id: int       │
│ - event_type: str       │
│ - location: str         │
│ - flight_id: int        │
│ - flight_number: str    │
│ - notes: str            │
│ - created_at: datetime  │
├─────────────────────────┤
│ + booking: Booking      │
└─────────────────────────┘
```

### 1.2 Service Layer

```
┌─────────────────────────────────────┐
│       BookingService                │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
│ - booking_repo: BookingRepository   │
│ - event_repo: EventRepository       │
├─────────────────────────────────────┤
│ + create_booking()                  │
│ + depart_booking()                  │
│ + arrive_booking()                  │
│ + cancel_booking()                  │
│ + get_booking()                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       RouteService                  │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
│ - flight_repo: FlightRepository     │
├─────────────────────────────────────┤
│ + search_routes()                   │
│ - _find_direct_flights()            │
│ - _find_transit_routes()            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       TrackingService               │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
│ - booking_repo: BookingRepository   │
│ - event_repo: EventRepository       │
├─────────────────────────────────────┤
│ + get_booking_history()             │
└─────────────────────────────────────┘
```

### 1.3 Repository Layer

```
┌─────────────────────────────────────┐
│     BookingRepository               │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
├─────────────────────────────────────┤
│ + create()                          │
│ + get_by_ref_id()                   │
│ + get_by_id()                       │
│ + update_status()                   │
│ + update_flight_ids()               │
│ + ref_id_exists()                   │
│ + get_recent_ref_ids()              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     FlightRepository                │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
├─────────────────────────────────────┤
│ + get_direct_flights()              │
│ + get_flights_from_origin()         │
│ + get_flights_to_destination()      │
│ + find_transit_routes()             │
│ + get_by_id()                       │
│ + get_by_ids()                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     EventRepository                 │
├─────────────────────────────────────┤
│ - db: AsyncSession                  │
├─────────────────────────────────────┤
│ + create()                          │
│ + get_by_booking_id()               │
└─────────────────────────────────────┘
```

---

## 2. SEQUENCE DIAGRAMS

### 2.1 Create Booking Sequence

```
User    Frontend    API      BookingService    BookingRepo    EventRepo    Database
 │          │        │              │               │             │            │
 │──Fill────>│       │              │               │             │            │
 │  Form    │       │              │               │             │            │
 │          │       │              │               │             │            │
 │<─────────│       │              │               │             │            │
 │ Validate │       │              │               │             │            │
 │          │       │              │               │             │            │
 │──Submit──>│      │              │               │             │            │
 │          │       │              │               │             │            │
 │          │──POST─>│             │               │             │            │
 │          │ /bookings            │               │             │            │
 │          │       │              │               │             │            │
 │          │       │──create()───>│               │             │            │
 │          │       │              │               │             │            │
 │          │       │              │──generate_ref_id()          │            │
 │          │       │              │               │             │            │
 │          │       │              │──create()────>│             │            │
 │          │       │              │               │             │            │
 │          │       │              │               │──INSERT────>│            │
 │          │       │              │               │  booking    │            │
 │          │       │              │               │             │            │
 │          │       │              │               │<────────────│            │
 │          │       │              │               │  booking    │            │
 │          │       │              │<──────────────│             │            │
 │          │       │              │               │             │            │
 │          │       │              │──create()────────────────>│            │
 │          │       │              │  BOOKED event              │            │
 │          │       │              │               │            │            │
 │          │       │              │               │            │──INSERT───>│
 │          │       │              │               │            │   event    │
 │          │       │              │               │            │            │
 │          │       │              │               │            │<───────────│
 │          │       │              │<──────────────────────────────          │
 │          │       │              │               │            │            │
 │          │       │<─────────────│               │            │            │
 │          │       │  BookingResponse             │            │            │
 │          │       │              │               │            │            │
 │          │<──────│              │               │            │            │
 │          │ 201 Created          │               │            │            │
 │          │              │               │            │            │
 │<─────────│              │               │            │            │
 │ Navigate to track page  │               │            │            │
```

### 2.2 Update Booking Status (Depart) Sequence

```
User    Frontend    API      BookingService    LockMgr    BookingRepo    EventRepo    Cache    Database
 │          │        │              │              │           │             │          │         │
 │──Click───>│       │              │              │           │             │          │         │
 │  Depart  │       │              │              │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │──POST─>│             │              │           │             │          │         │
 │          │ /depart│             │              │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │──depart()───>│              │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──acquire()──>│           │             │          │         │
 │          │       │              │  lock:ACB123 │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │<─────────────│           │             │          │         │
 │          │       │              │  Lock OK     │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──get_by_ref_id()────────>│             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │              │           │──SELECT────>│          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │              │           │<────────────│          │         │
 │          │       │              │<─────────────────────────│             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──validate_state()        │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──update_status()────────>│             │          │         │
 │          │       │              │  DEPARTED    │           │             │          │         │
 │          │       │              │              │           │──UPDATE────>│          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │              │           │<────────────│          │         │
 │          │       │              │<─────────────────────────│             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──create()────────────────────────────>│          │         │
 │          │       │              │  DEPARTED event          │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │              │           │             │──INSERT─>│         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │              │           │             │<─────────│         │
 │          │       │              │<─────────────────────────────────────────        │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──delete()──────────────────────────────────────>│         │
 │          │       │              │  cache:booking:ACB123    │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │──release()──>│           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │       │              │<─────────────│           │             │          │         │
 │          │       │<─────────────│              │           │             │          │         │
 │          │       │  BookingResponse            │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │          │<──────│              │              │           │             │          │         │
 │          │ 200 OK│              │              │           │             │          │         │
 │          │       │              │              │           │             │          │         │
 │<─────────│       │              │              │           │             │          │         │
 │ UI Update│       │              │              │           │             │          │         │
```

### 2.3 Route Search Sequence

```
User    Frontend    API      RouteService    Cache    FlightRepo    Database
 │          │        │              │           │           │            │
 │──Enter───>│       │              │           │           │            │
 │  Search  │       │              │           │           │            │
 │  Params  │       │              │           │           │            │
 │          │       │              │           │           │            │
 │──Submit──>│      │              │           │           │            │
 │          │       │              │           │           │            │
 │          │──POST─>│             │           │           │            │
 │          │ /search│             │           │           │            │
 │          │       │              │           │           │            │
 │          │       │──search()───>│           │           │            │
 │          │       │              │           │           │            │
 │          │       │              │──get()───>│           │            │
 │          │       │              │  cache key│           │            │
 │          │       │              │           │           │            │
 │          │       │              │<──────────│           │            │
 │          │       │              │  Cache Miss           │            │
 │          │       │              │           │           │            │
 │          │       │              │──get_direct_flights()─>│            │
 │          │       │              │           │           │            │
 │          │       │              │           │           │──SELECT───>│
 │          │       │              │           │           │  direct    │
 │          │       │              │           │           │            │
 │          │       │              │           │           │<───────────│
 │          │       │              │<──────────────────────│            │
 │          │       │              │  direct_flights       │            │
 │          │       │              │           │           │            │
 │          │       │              │──find_transit_routes()>│            │
 │          │       │              │           │           │            │
 │          │       │              │           │           │──SELECT───>│
 │          │       │              │           │           │  first leg │
 │          │       │              │           │           │            │
 │          │       │              │           │           │<───────────│
 │          │       │              │           │           │            │
 │          │       │              │           │           │──SELECT───>│
 │          │       │              │           │           │  second leg│
 │          │       │              │           │           │            │
 │          │       │              │           │           │<───────────│
 │          │       │              │<──────────────────────│            │
 │          │       │              │  transit_routes       │            │
 │          │       │              │           │           │            │
 │          │       │              │──set()───>│           │            │
 │          │       │              │  cache    │           │            │
 │          │       │              │  TTL=3600 │           │            │
 │          │       │              │           │           │            │
 │          │       │              │<──────────│           │            │
 │          │       │<─────────────│           │           │            │
 │          │       │  RouteResponse           │           │            │
 │          │       │              │           │           │            │
 │          │<──────│              │           │           │            │
 │          │ 200 OK│              │           │           │            │
 │          │       │              │           │           │            │
 │<─────────│       │              │           │           │            │
 │ Display  │       │              │           │           │            │
 │ Routes   │       │              │           │           │            │
```

---

## 3. API SPECIFICATIONS

### 3.1 Create Booking

**Endpoint**: `POST /api/v1/bookings`

**Request Body**:
```json
{
  "origin": "DEL",
  "destination": "BLR",
  "pieces": 10,
  "weight_kg": 500,
  "flight_ids": [1, 2]  // Optional
}
```

**Validation Rules**:
- origin: Required, 3-10 characters, uppercase
- destination: Required, 3-10 characters, uppercase, must differ from origin
- pieces: Required, integer > 0
- weight_kg: Required, integer > 0
- flight_ids: Optional array of integers

**Response** (201 Created):
```json
{
  "id": 1,
  "ref_id": "ACB12A4D",
  "origin": "DEL",
  "destination": "BLR",
  "pieces": 10,
  "weight_kg": 500,
  "status": "BOOKED",
  "flight_ids": [1, 2],
  "created_at": "2025-11-23T07:35:42Z",
  "updated_at": "2025-11-23T07:35:42Z"
}
```

**Error Responses**:
- 400: Validation error (e.g., origin == destination)
- 500: Server error

---

### 3.2 Depart Booking

**Endpoint**: `POST /api/v1/bookings/{ref_id}/depart`

**Path Parameter**:
- ref_id: Booking reference ID (e.g., ACB12A4D)

**Request Body**:
```json
{
  "location": "DEL",
  "flight_id": 1,  // Optional
  "flight_number": "AI101",  // Optional
  "notes": "Departed on time"  // Optional
}
```

**Validation Rules**:
- location: Required, 3-10 characters, uppercase
- flight_id: Optional integer
- flight_number: Optional string, max 20 characters
- notes: Optional string

**Response** (200 OK):
```json
{
  "id": 1,
  "ref_id": "ACB12A4D",
  "origin": "DEL",
  "destination": "BLR",
  "pieces": 10,
  "weight_kg": 500,
  "status": "DEPARTED",
  "flight_ids": [1, 2],
  "created_at": "2025-11-23T07:35:42Z",
  "updated_at": "2025-11-23T08:00:00Z"
}
```

**Error Responses**:
- 400: Invalid state transition (already departed, cancelled)
- 404: Booking not found
- 409: Concurrent update conflict (retry)
- 500: Server error

---

### 3.3 Arrive Booking

**Endpoint**: `POST /api/v1/bookings/{ref_id}/arrive`

**Path Parameter**:
- ref_id: Booking reference ID

**Request Body**:
```json
{
  "location": "BLR",
  "flight_id": 2,
  "flight_number": "AI102",
  "notes": "Arrived safely"
}
```

**Validation Rules**: Same as Depart

**Response** (200 OK): Booking object with status="ARRIVED"

**Error Responses**: Same as Depart

---

### 3.4 Cancel Booking

**Endpoint**: `DELETE /api/v1/bookings/{ref_id}`

**Path Parameter**:
- ref_id: Booking reference ID

**Response** (200 OK): Booking object with status="CANCELLED"

**Error Responses**:
- 400: Cannot cancel (already arrived)
- 404: Booking not found
- 409: Concurrent update conflict
- 500: Server error

---

### 3.5 Get Booking

**Endpoint**: `GET /api/v1/bookings/{ref_id}`

**Path Parameter**:
- ref_id: Booking reference ID

**Response** (200 OK): Booking object

**Error Responses**:
- 404: Booking not found
- 500: Server error

---

### 3.6 Get Booking History

**Endpoint**: `GET /api/v1/bookings/{ref_id}/history`

**Path Parameter**:
- ref_id: Booking reference ID

**Response** (200 OK):
```json
{
  "booking": {
    "id": 1,
    "ref_id": "ACB12A4D",
    "origin": "DEL",
    "destination": "BLR",
    "pieces": 10,
    "weight_kg": 500,
    "status": "ARRIVED",
    "flight_ids": [1, 2],
    "created_at": "2025-11-23T07:35:42Z",
    "updated_at": "2025-11-23T10:00:00Z"
  },
  "timeline": [
    {
      "id": 1,
      "event_type": "BOOKED",
      "location": "DEL",
      "flight_id": null,
      "flight_number": null,
      "notes": "Booking created",
      "created_at": "2025-11-23T07:35:42Z"
    },
    {
      "id": 2,
      "event_type": "DEPARTED",
      "location": "DEL",
      "flight_id": 1,
      "flight_number": "AI101",
      "notes": "Departed on time",
      "created_at": "2025-11-23T08:00:00Z"
    },
    {
      "id": 3,
      "event_type": "ARRIVED",
      "location": "BLR",
      "flight_id": 2,
      "flight_number": "AI102",
      "notes": "Arrived safely",
      "created_at": "2025-11-23T10:00:00Z"
    }
  ]
}
```

**Error Responses**:
- 404: Booking not found
- 500: Server error

---

### 3.7 Search Routes

**Endpoint**: `POST /api/v1/routes/search`

**Request Body**:
```json
{
  "origin": "DEL",
  "destination": "BLR",
  "departure_date": "2025-12-01"
}
```

**Validation Rules**:
- origin: Required, 3-10 characters
- destination: Required, 3-10 characters
- departure_date: Required, ISO date format (YYYY-MM-DD)

**Response** (200 OK):
```json
{
  "origin": "DEL",
  "destination": "BLR",
  "departure_date": "2025-12-01",
  "direct_flights": [
    {
      "id": 1,
      "flight_number": "AI101",
      "airline_name": "Air India",
      "departure_datetime": "2025-12-01T06:00:00Z",
      "arrival_datetime": "2025-12-01T09:00:00Z",
      "origin": "DEL",
      "destination": "BLR",
      "created_at": "2025-11-20T00:00:00Z",
      "updated_at": "2025-11-20T00:00:00Z"
    }
  ],
  "transit_routes": [
    {
      "route_type": "transit",
      "flights": [
        {
          "id": 2,
          "flight_number": "AI201",
          "airline_name": "Air India",
          "departure_datetime": "2025-12-01T07:00:00Z",
          "arrival_datetime": "2025-12-01T09:30:00Z",
          "origin": "DEL",
          "destination": "HYD",
          "created_at": "2025-11-20T00:00:00Z",
          "updated_at": "2025-11-20T00:00:00Z"
        },
        {
          "id": 3,
          "flight_number": "AI202",
          "airline_name": "Air India",
          "departure_datetime": "2025-12-01T11:00:00Z",
          "arrival_datetime": "2025-12-01T12:15:00Z",
          "origin": "HYD",
          "destination": "BLR",
          "created_at": "2025-11-20T00:00:00Z",
          "updated_at": "2025-11-20T00:00:00Z"
        }
      ],
      "total_duration_hours": 5.25,
      "transit_airport": "HYD"
    }
  ]
}
```

**Error Responses**:
- 400: Validation error
- 500: Server error

---

## 4. DATABASE QUERY OPTIMIZATION

### 4.1 Get Booking by ref_id

**Query**:
```sql
SELECT * FROM bookings WHERE ref_id = 'ACB12A4D';
```

**Index Used**: `idx_bookings_ref_id` (Unique B-Tree)

**Complexity**: O(log n)

**Expected Performance**: < 5ms for millions of records

---

### 4.2 Direct Flight Search

**Query**:
```sql
SELECT *
FROM flights
WHERE origin = 'DEL'
  AND destination = 'BLR'
  AND departure_datetime >= '2025-12-01 00:00:00+00'
  AND departure_datetime <= '2025-12-01 23:59:59+00'
ORDER BY departure_datetime;
```

**Index Used**: `idx_flights_route_date` (origin, destination, departure_datetime)

**Complexity**: O(log n + k) where k = result count

**Expected Performance**: < 10ms for ~10 results

---

### 4.3 Transit Route Search - First Leg

**Query**:
```sql
SELECT *
FROM flights
WHERE origin = 'DEL'
  AND departure_datetime >= '2025-12-01 00:00:00+00'
  AND departure_datetime <= '2025-12-01 23:59:59+00'
ORDER BY departure_datetime;
```

**Index Used**: `idx_flights_origin` + `idx_flights_departure`

**Expected Performance**: < 20ms

---

### 4.3 Transit Route Search - Second Leg

**Query**:
```sql
SELECT *
FROM flights
WHERE destination = 'BLR'
  AND origin = 'HYD'
  AND departure_datetime >= '2025-12-01 11:30:00+00'
  AND departure_datetime <= '2025-12-02 23:59:59+00'
ORDER BY departure_datetime;
```

**Index Used**: `idx_flights_route_date`

**Expected Performance**: < 20ms

**Total Transit Search**: < 50ms (including nested loop)

---

### 4.4 Get Booking History

**Query**:
```sql
SELECT b.*, e.*
FROM bookings b
LEFT JOIN booking_events e ON e.booking_id = b.id
WHERE b.ref_id = 'ACB12A4D'
ORDER BY e.created_at ASC;
```

**Index Used**:
- `idx_bookings_ref_id` for booking lookup
- `idx_booking_events_booking_id` for events

**Complexity**: O(log n + m) where m = event count

**Expected Performance**: < 10ms for typical bookings

---

## 5. ALGORITHM DETAILS

### 5.1 Reference ID Generation Algorithm

**Function**: `generate_ref_id()`

**Algorithm**:
```python
def generate_ref_id() -> str:
    """
    Generate human-friendly reference ID
    Format: ACB + 5 alphanumeric characters (uppercase)
    """
    prefix = "ACB"
    charset = string.ascii_uppercase + string.digits  # A-Z, 0-9 = 36 chars
    random_part = ''.join(random.choices(charset, k=5))
    return prefix + random_part

# Total combinations = 36^5 = 60,466,176
# Collision probability (birthday paradox):
#   For 50K bookings/day: ~0.01% collision per day
#   Use collision check to ensure uniqueness
```

**Collision Handling**:
```python
async def generate_unique_ref_id(existing_ids: set) -> str:
    max_attempts = 100
    
    for _ in range(max_attempts):
        ref_id = generate_ref_id()
        if ref_id not in existing_ids:
            return ref_id
    
    # Fallback with timestamp
    timestamp = datetime.utcnow().strftime("%H%M%S")
    return f"ACB{timestamp[:5]}"
```

**Time Complexity**: O(1) expected, O(k) worst case where k = attempts

---

### 5.2 Transit Route Finding Algorithm

**Function**: `find_transit_routes()`

**Algorithm**:
```python
async def find_transit_routes(origin, destination, departure_date):
    """
    Find one-hop transit routes
    Constraint: Second hop must be same day or next day
    """
    
    # Step 1: Get all first leg flights from origin
    first_leg_flights = await get_flights_from_origin(origin, departure_date)
    
    transit_routes = []
    
    # Step 2: For each first leg, find connecting flights
    for first_flight in first_leg_flights:
        transit_airport = first_flight.destination
        
        # Skip if transit is final destination
        if transit_airport == destination:
            continue
        
        # Calculate connection window
        min_connection_time = timedelta(hours=2)
        earliest_departure = first_flight.arrival_datetime + min_connection_time
        latest_departure = datetime.combine(
            departure_date + timedelta(days=1),
            datetime.max.time()
        )
        
        # Step 3: Find second leg flights
        second_leg_flights = await get_flights_to_destination(
            destination,
            earliest_departure,
            latest_departure
        )
        
        # Step 4: Match flights with same transit airport
        for second_flight in second_leg_flights:
            if second_flight.origin == transit_airport:
                transit_routes.append((first_flight, second_flight))
    
    return transit_routes
```

**Time Complexity**:
- Get first leg: O(log n + k1) where k1 = flights from origin
- For each first leg (k1):
  - Get second leg: O(log n + k2) where k2 = flights to destination
- Total: O(k1 * (log n + k2))
- Typical: k1 ≈ 50, k2 ≈ 10 → O(500 log n)

**Space Complexity**: O(k1 * k2) for storing routes

**Optimization**:
- Index on (origin, destination, departure_datetime)
- Filter in database instead of application
- Cache results for 1 hour

---

### 5.3 Distributed Lock Algorithm (Redlock)

**Implementation**:
```python
class DistributedLock:
    async def acquire(self) -> bool:
        """
        Acquire lock using SET NX EX command
        """
        lock_id = str(uuid.uuid4())  # Unique lock owner
        
        for attempt in range(retry_times):
            # Atomic operation: SET key value NX EX timeout
            result = await redis.set(
                self.resource,
                lock_id,
                nx=True,  # Only set if not exists
                ex=self.timeout  # Expiration time in seconds
            )
            
            if result:
                self.lock_id = lock_id
                return True
            
            # Wait before retry
            await asyncio.sleep(retry_delay)
        
        return False
    
    async def release(self) -> bool:
        """
        Release lock using Lua script (atomic check-and-delete)
        """
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await redis.eval(lua_script, 1, self.resource, self.lock_id)
        return result == 1
```

**Properties**:
- **Mutual Exclusion**: Only one client holds lock at a time
- **Deadlock Free**: Lock auto-expires after timeout
- **Fault Tolerance**: Works even if client crashes
- **Safety**: Check lock ownership before release

**Time Complexity**:
- Acquire: O(1) per attempt, O(k) for k retries
- Release: O(1)

---

## 6. STATE MACHINE

### 6.1 Booking Status State Machine

```
                    ┌──────────┐
                    │  BOOKED  │ (Initial State)
                    └─────┬────┘
                          │
              ┌───────────┼───────────┐
              │                       │
              ▼                       ▼
        ┌──────────┐            ┌────────────┐
        │ DEPARTED │            │ CANCELLED  │
        └─────┬────┘            └────────────┘
              │                  (Terminal State)
              │
              ▼
        ┌──────────┐
        │ ARRIVED  │
        └─────┬────┘
              │
              ▼
        ┌───────────┐
        │ DELIVERED │
        └───────────┘
       (Terminal State)
```

### 6.2 Valid State Transitions

| From | To | Allowed | Notes |
|------|------|---------|-------|
| BOOKED | DEPARTED | ✅ | Normal flow |
| BOOKED | CANCELLED | ✅ | Before shipping |
| BOOKED | ARRIVED | ✅ | Direct arrival (skip departed) |
| DEPARTED | ARRIVED | ✅ | Normal flow |
| DEPARTED | CANCELLED | ✅ | Can cancel in transit |
| DEPARTED | DELIVERED | ✅ | Skip arrived |
| ARRIVED | DELIVERED | ✅ | Final delivery |
| ARRIVED | CANCELLED | ❌ | Cannot cancel after arrival |
| CANCELLED | * | ❌ | Terminal state |
| DELIVERED | * | ❌ | Terminal state |

### 6.3 Validation Logic

```python
def validate_state_transition(current_status: str, new_status: str) -> bool:
    """Validate if state transition is allowed"""
    
    # Cannot change from terminal states
    if current_status in ['CANCELLED', 'DELIVERED']:
        return False
    
    # Cannot cancel after arrival
    if new_status == 'CANCELLED' and current_status == 'ARRIVED':
        return False
    
    # All other transitions allowed
    return True
```

---

## 7. CACHING IMPLEMENTATION

### 7.1 Cache Key Design

**Format**: `{entity}:{identifier}:{optional_params}`

**Examples**:
- `route:DEL:BLR:2025-12-01`
- `booking:ACB12A4D`
- `booking_history:ACB12A4D`

**Benefits**:
- Consistent naming convention
- Easy pattern matching for invalidation
- Human-readable for debugging

---

### 7.2 Cache Aside Pattern

```python
async def get_booking(ref_id: str) -> Booking:
    """Get booking with cache-aside pattern"""
    
    cache_key = f"booking:{ref_id}"
    
    # 1. Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return Booking(**cached)
    
    # 2. Cache miss - query database
    booking = await db.query(Booking).filter_by(ref_id=ref_id).first()
    
    if not booking:
        raise NotFound()
    
    # 3. Store in cache
    await cache.set(cache_key, booking.dict(), ttl=300)
    
    return booking
```

---

### 7.3 Cache Invalidation Strategy

**Write-Through Invalidation**:
```python
async def update_booking_status(booking_id: int, status: str):
    """Update booking and invalidate cache"""
    
    # 1. Update database
    booking = await db.query(Booking).get(booking_id)
    booking.status = status
    await db.commit()
    
    # 2. Invalidate related caches
    await cache.delete(f"booking:{booking.ref_id}")
    await cache.delete(f"booking_history:{booking.ref_id}")
    
    return booking
```

**Pattern-Based Invalidation**:
```python
async def invalidate_booking_caches(ref_id: str):
    """Invalidate all caches related to a booking"""
    
    pattern = f"booking*:{ref_id}"
    deleted_count = await cache.delete_pattern(pattern)
    
    logger.info(f"Invalidated {deleted_count} cache keys for {ref_id}")
```

---

## 8. ERROR HANDLING

### 8.1 Exception Hierarchy

```
Exception
├── HTTPException (FastAPI)
│   ├── 400 Bad Request
│   │   └── ValidationError
│   ├── 404 Not Found
│   ├── 409 Conflict
│   │   └── ConcurrentUpdateError
│   └── 500 Internal Server Error
│
├── DatabaseError
│   ├── ConnectionError
│   └── IntegrityError
│
└── CacheError
    └── ConnectionError
```

### 8.2 Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### 8.3 Error Handling Examples

**Validation Error**:
```python
if booking_data.origin == booking_data.destination:
    raise HTTPException(
        status_code=400,
        detail="Origin and destination must be different"
    )
```

**Not Found**:
```python
booking = await booking_repo.get_by_ref_id(ref_id)
if not booking:
    raise HTTPException(
        status_code=404,
        detail=f"Booking not found: {ref_id}"
    )
```

**Concurrent Update**:
```python
try:
    async with lock:
        # Update booking
        pass
except TimeoutError:
    raise HTTPException(
        status_code=409,
        detail="Booking is being updated. Please try again."
    )
```

**Database Error**:
```python
try:
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    raise HTTPException(
        status_code=400,
        detail="Database constraint violation"
    )
```

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests

**Scope**: Individual functions and methods

**Examples**:
- `test_generate_ref_id_format()` - Verify ref_id format
- `test_generate_ref_id_uniqueness()` - Test collision avoidance
- `test_create_booking()` - Test booking creation logic
- `test_invalid_state_transition()` - Test validation logic

**Tools**: pytest, pytest-asyncio, unittest.mock

---

### 9.2 Integration Tests

**Scope**: Multiple components working together

**Examples**:
- `test_create_and_retrieve_booking()` - Create and fetch from DB
- `test_booking_state_transitions()` - Full booking lifecycle
- `test_route_search_with_cache()` - Route search + caching

**Tools**: pytest, test database, test