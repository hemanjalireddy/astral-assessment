import uvicorn
from fastapi import FastAPI
import inngest
import inngest.fast_api

from api.routers import health, register
from features.extraction.processor import inngest_client, process_registration

# Initialize FastAPI app
app = FastAPI(
    title="Astral Assessment API",
    description="AI-powered business intelligence pipeline",
    version="0.1.0",
)

# Include your API routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(register.router, tags=["registration"])

# Serve Inngest functions as webhook routes
inngest.fast_api.serve(
    app,
    inngest_client,
    functions=[process_registration]  # your existing Inngest function
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
