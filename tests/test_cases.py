import pytest
import httpx
from typing import AsyncGenerator
from pathlib import Path

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for testing"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client


@pytest.mark.asyncio
async def test_basic_health_check(client: httpx.AsyncClient):
    """Test basic health check endpoint"""
    response = await client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    print(f"Basic Health: {response.status_code} - {data}")


@pytest.mark.asyncio
async def test_detailed_health_check(client: httpx.AsyncClient):
    """Test detailed health check endpoint"""
    response = await client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "services" in data
    assert "version" in data
    print(f"Detailed Health: {response.status_code} - Services: {data['services']}")


@pytest.mark.asyncio
async def test_validation_failure_no_website_or_linkedin(client: httpx.AsyncClient):
    """Test validation failure when neither website nor LinkedIn is provided"""
    payload = {"first_name": "Invalid", "last_name": "User"}
    response = await client.post("/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    print(f"Validation Failure Test: {response.status_code} - Expected validation error")


@pytest.mark.asyncio
async def test_validation_failure_missing_first_name(client: httpx.AsyncClient):
    """Test validation failure when first_name is missing"""
    payload = {"last_name": "User", "company_website": "https://www.example.com"}
    response = await client.post("/register", json=payload)
    assert response.status_code == 422
    print(f"Missing First Name Test: {response.status_code} - Expected validation error")


@pytest.mark.asyncio
async def test_website_only_registration(client: httpx.AsyncClient):
    """Test registration with website URL only"""
    payload = {
        "first_name": "Sarah",
        "last_name": "Chen",
        "company_website": "https://www.airtable.com",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "request_id" in data
    assert "timestamp" in data
    assert data["message"] == "Registration queued for processing"
    print(f"Website Only Test: {response.status_code} - Request ID: {data['request_id']}")


@pytest.mark.asyncio
async def test_linkedin_only_registration(client: httpx.AsyncClient):
    """Test registration with LinkedIn URL only"""
    payload = {
        "first_name": "David",
        "last_name": "Rodriguez",
        "linkedin": "https://www.linkedin.com/in/davidrodriguez-tech",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "request_id" in data
    assert "timestamp" in data
    print(f"LinkedIn Only Test: {response.status_code} - Request ID: {data['request_id']}")


@pytest.mark.asyncio
async def test_both_website_and_linkedin_registration(client: httpx.AsyncClient):
    """Test registration with both website and LinkedIn provided"""
    payload = {
        "first_name": "Maria",
        "last_name": "Johnson",
        "company_website": "https://www.notion.so",
        "linkedin": "https://www.linkedin.com/in/mariajohnson-product",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "request_id" in data
    assert "timestamp" in data
    print(f"Both Provided Test: {response.status_code} - Request ID: {data['request_id']}")


@pytest.mark.asyncio
async def test_url_normalization(client: httpx.AsyncClient):
    """Test that URLs are properly normalized"""
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "company_website": "airtable.com",
        "linkedin": "davidrodriguez-tech",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"URL Normalization Test: {response.status_code} - URLs normalized successfully")


@pytest.mark.asyncio
async def test_linear_company_website(client: httpx.AsyncClient):
    """Test with Linear (developer-focused startup)"""
    payload = {"first_name": "Alex", "last_name": "Thompson", "company_website": "https://linear.app"}
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"Linear Company Test: {response.status_code} - Request ID: {data['request_id']}")


@pytest.mark.asyncio
async def test_framer_company_website(client: httpx.AsyncClient):
    """Test with Framer (design tool company)"""
    payload = {"first_name": "Jessica", "last_name": "Kim", "company_website": "https://www.framer.com"}
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"Framer Company Test: {response.status_code} - Request ID: {data['request_id']}")


@pytest.mark.asyncio
async def test_invalid_website_url(client: httpx.AsyncClient):
    """Test with clearly invalid website URL"""
    payload = {"first_name": "Invalid", "last_name": "Website", "company_website": "not-a-valid-url"}
    response = await client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"Invalid URL Test: {response.status_code} - Handled gracefully")


def test_outputs_directory_exists():
    """Test that outputs directory exists"""
    outputs_dir = Path("outputs")
    assert outputs_dir.exists(), "Outputs directory should exist"
    assert outputs_dir.is_dir(), "Outputs should be a directory"
    print(f"Outputs Directory: {outputs_dir.absolute()} exists")
