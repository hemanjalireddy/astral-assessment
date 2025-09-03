import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.types import RegisterRequest, RegisterResponse
from features.extraction.processor import trigger_analysis

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse)
async def register_prospect(request: RegisterRequest) -> RegisterResponse:
    """
    Register a new prospect for analysis
    
    This endpoint validates the request and triggers asynchronous processing
    via Inngest. It returns immediately while the heavy processing happens
    in the background.
    """
    try:
        logger.info(f"Received registration for: {request.first_name} {request.last_name}")
        
        # Trigger async processing
        request_id = await trigger_analysis(request)
        
        return RegisterResponse(
            success=True,
            message="Registration queued for processing",
            request_id=request_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to process registration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue registration for processing: {str(e)}"
        )