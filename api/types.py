"""
Pydantic models for API request/response validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
import uuid

from pydantic import BaseModel, Field, model_validator


class RegisterRequest(BaseModel):
    """Request model for the /register endpoint"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_website: Optional[str] = Field(None, max_length=500)
    linkedin: Optional[str] = Field(None, max_length=500)
    
    @model_validator(mode='after')
    def validate_at_least_one_provided(self) -> 'RegisterRequest':
        """Ensure at least one of company_website or linkedin is provided"""
        if not self.company_website and not self.linkedin:
            raise ValueError('At least one of company_website or linkedin must be provided')
        return self
    
    def model_post_init(self, __context) -> None:
        """Post-initialization validation and URL normalization"""
        if self.company_website and not (self.company_website.startswith('http://') or self.company_website.startswith('https://')):
            self.company_website = f"https://{self.company_website}"
        
        if self.linkedin and not self.linkedin.startswith('http'):
            # Handle various LinkedIn URL formats
            if self.linkedin.startswith('linkedin.com') or self.linkedin.startswith('www.linkedin.com'):
                self.linkedin = f"https://{self.linkedin}"
            elif not self.linkedin.startswith('linkedin.com'):
                self.linkedin = f"https://linkedin.com/in/{self.linkedin}"


class RegisterResponse(BaseModel):
    """Response model for successful registration"""
    success: bool = True
    message: str = "Registration queued for processing"
    request_id: str
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response"""
    version: str = "0.1.0"
    uptime_seconds: float
    services: Dict[str, str] = Field(default_factory=lambda: {
        "inngest": "unknown",
        "firecrawl": "unknown"
    })


class LinkedInAnalysis(BaseModel):
    """LinkedIn analysis results (placeholder for implementation plan)"""
    status: str = "not_implemented"
    implementation_plan: Optional[str] = None


class WebsiteAnalysis(BaseModel):
    """Website analysis results"""
    discovered_urls: List[str] = Field(default_factory=list)
    filtered_urls: List[str] = Field(default_factory=list)
    filtering_logic: Optional[str] = None
    scraped_content: Dict[str, str] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class AnalysisOutput(BaseModel):
    """Complete analysis output for JSON file generation"""
    request_id: str
    timestamp: datetime
    input_data: RegisterRequest
    linkedin_analysis: LinkedInAnalysis
    website_analysis: WebsiteAnalysis