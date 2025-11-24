import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import get_db
from tests.conftest import db_session


@pytest.mark.asyncio
async def test_complete_booking_flow_via_api(db_session):
    """Test complete booking flow through API endpoints"""
    
    # Override database dependency to use test database
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "origin": "DEL",
                "destination": "BLR",
                "pieces": 10,
                "weight_kg": 500
            }
        )
        assert create_response.status_code == 201
        booking = create_response.json()
        ref_id = booking["ref_id"]
        assert booking["status"] == "BOOKED"
        
        # 2. Get booking
        get_response = await client.get(f"/api/v1/bookings/{ref_id}")
        assert get_response.status_code == 200
        assert get_response.json()["ref_id"] == ref_id
        
        # 3. Depart booking
        depart_response = await client.post(
            f"/api/v1/bookings/{ref_id}/depart",
            json={
                "location": "DEL",
                "flight_number": "AI101",
                "notes": "Departed on time"
            }
        )
        assert depart_response.status_code == 200
        assert depart_response.json()["status"] == "DEPARTED"
        
        # 4. Arrive booking
        arrive_response = await client.post(
            f"/api/v1/bookings/{ref_id}/arrive",
            json={
                "location": "BLR",
                "flight_number": "AI101",
                "notes": "Arrived safely"
            }
        )
        assert arrive_response.status_code == 200
        assert arrive_response.json()["status"] == "ARRIVED"
        
        # 5. Deliver booking
        deliver_response = await client.post(
            f"/api/v1/bookings/{ref_id}/deliver",
            json={
                "location": "BLR",
                "notes": "Delivered to customer"
            }
        )
        assert deliver_response.status_code == 200
        assert deliver_response.json()["status"] == "DELIVERED"
        
        # 6. Get booking history
        history_response = await client.get(f"/api/v1/bookings/{ref_id}/history")
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history["timeline"]) == 4
        assert history["timeline"][0]["event_type"] == "BOOKED"
        assert history["timeline"][1]["event_type"] == "DEPARTED"
        assert history["timeline"][2]["event_type"] == "ARRIVED"
        assert history["timeline"][3]["event_type"] == "DELIVERED"


@pytest.mark.asyncio
async def test_route_search_via_api(db_session):
    """Test route search through API"""
    
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/routes/search",
            json={
                "origin": "DEL",
                "destination": "BLR",
                "departure_date": "2025-12-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["origin"] == "DEL"
        assert data["destination"] == "BLR"
        assert "direct_flights" in data
        assert "transit_routes" in data


@pytest.mark.asyncio
async def test_cancel_booking_via_api(db_session):
    """Test booking cancellation through API"""
    
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "origin": "DEL",
                "destination": "BLR",
                "pieces": 5,
                "weight_kg": 250
            }
        )
        ref_id = create_response.json()["ref_id"]
        
        # Cancel booking
        cancel_response = await client.delete(f"/api/v1/bookings/{ref_id}")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_invalid_status_transitions(db_session):
    """Test that invalid status transitions are rejected"""
    
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create and arrive booking
        create_response = await client.post(
            "/api/v1/bookings",
            json={
                "origin": "DEL",
                "destination": "BLR",
                "pieces": 5,
                "weight_kg": 250
            }
        )
        ref_id = create_response.json()["ref_id"]
        
        await client.post(
            f"/api/v1/bookings/{ref_id}/arrive",
            json={"location": "BLR"}
        )
        
        # Try to cancel after arrival - should fail
        cancel_response = await client.delete(f"/api/v1/bookings/{ref_id}")
        assert cancel_response.status_code == 400
        
        # Try to deliver without arriving first
        create_response2 = await client.post(
            "/api/v1/bookings",
            json={
                "origin": "DEL",
                "destination": "BLR",
                "pieces": 5,
                "weight_kg": 250
            }
        )
        ref_id2 = create_response2.json()["ref_id"]
        
        deliver_response = await client.post(
            f"/api/v1/bookings/{ref_id2}/deliver",
            json={"location": "BLR"}
        )
        assert deliver_response.status_code == 400


@pytest.mark.asyncio
async def test_health_check(db_session):
    """Test health check endpoint"""
    
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_booking_not_found(db_session):
    """Test 404 for non-existent booking"""
    
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/bookings/INVALID123")
        assert response.status_code == 404
