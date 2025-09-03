import time
from datetime import datetime

from fastapi import APIRouter

from api.types import DetailedHealthResponse, HealthResponse

router = APIRouter()

# Track startup time for uptime calculation
_startup_time = time.time()


@router.get("/", response_model=HealthResponse)
async def basic_health() -> HealthResponse:
    """Basic health check endpoint"""
    return HealthResponse()


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health() -> DetailedHealthResponse:
    """Detailed health check with service status"""
    current_time = time.time()
    uptime = current_time - _startup_time
    
    # TODO: Add actual service health checks
    services = {
        "inngest": "operational",  # Would check Inngest connectivity
        "firecrawl": "operational"  # Would check Firecrawl API status
    }
    
    return DetailedHealthResponse(
        uptime_seconds=uptime,
        services=services
    )