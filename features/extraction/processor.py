import json
import uuid
from datetime import datetime
from loguru import logger
from pathlib import Path
import inngest

from api.types import AnalysisOutput, LinkedInAnalysis, RegisterRequest, WebsiteAnalysis
from core.clients.firecrawl import FirecrawlClient
from core.config.settings import settings
from features.extraction.linkedin_analysis import get_linkedin_implementation_plan


# Initialize Inngest client
inngest_client = inngest.Inngest(
    app_id="astral-assessment",
    event_key=settings.inngest_event_key,
    signing_key=settings.inngest_signing_key,
    logger=logger.bind(name="inngest"),
)

# Inngest function to process registration
@inngest_client.create_function(
    fn_id="process-registration",
    trigger=inngest.TriggerEvent(event="registration.submitted")
)
async def process_registration(ctx: inngest.Context):
    logger.info(f"Processing registration: {ctx.event.data}")

    request_data = ctx.event.data
    request_id = request_data.get("request_id")
    timestamp = datetime.fromisoformat(request_data.get("timestamp"))
    register_request = RegisterRequest(**request_data.get("input_data"))

    linkedin_analysis = LinkedInAnalysis(
        status="not_implemented",
        implementation_plan=get_linkedin_implementation_plan()
    )
    website_analysis = WebsiteAnalysis()

    if register_request.company_website:
        website_analysis_data = await ctx.step.run(
            "analyze-website",
            analyze_website,
            register_request.company_website
        )
        # Convert back to Pydantic if needed
        website_analysis = WebsiteAnalysis(**website_analysis_data)
    analysis_output = AnalysisOutput(
        request_id=request_id,
        timestamp=timestamp,
        input_data=register_request,
        linkedin_analysis=linkedin_analysis,
        website_analysis=website_analysis
    )

    await ctx.step.run("save-analysis", save_analysis_output, analysis_output)
    logger.info(f"Completed processing for request_id: {request_id}")
    return {"status": "completed", "request_id": request_id}


# Website analysis helper
async def analyze_website(website_url: str) -> dict:
    logger.info(f"Starting website analysis for: {website_url}")
    firecrawl = FirecrawlClient()
    analysis = WebsiteAnalysis()

    try:
        discovered_urls = await firecrawl.discover_urls(website_url)
        analysis.discovered_urls = discovered_urls

        filtered_urls = firecrawl.filter_valuable_urls(discovered_urls)
        analysis.filtered_urls = filtered_urls
        analysis.filtering_logic = (
            f"Filtered {len(discovered_urls)} URLs to {len(filtered_urls)} high-value URLs"
        )

        if filtered_urls:
            scraped_content = await firecrawl.scrape_multiple_urls(filtered_urls)
            analysis.scraped_content = scraped_content

    except Exception as e:
        error_msg = f"Error analyzing website {website_url}: {str(e)}"
        logger.error(error_msg)
        analysis.errors.append(error_msg)

    # Convert Pydantic model to dict for JSON serialization
    return analysis.model_dump() 



# Save analysis output to JSON
async def save_analysis_output(analysis_output: AnalysisOutput) -> None:
    timestamp_str = analysis_output.timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp_str}.json"
    filepath = settings.output_dir / filename

    try:
        output_dict = analysis_output.model_dump()  # Pydantic v2
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"Analysis saved to: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save analysis output: {e}")
        raise


# Trigger the analysis programmatically
async def trigger_analysis(register_request: RegisterRequest) -> str:
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()

    # Convert Pydantic model to dict
    input_data = register_request.model_dump()

    # Wrap data in an Inngest.Event
    event = inngest.Event(
        name="registration.submitted",
        data={
            "request_id": request_id,
            "timestamp": timestamp.isoformat(),
            "input_data": input_data
        }
    )

    logger.info(f"Triggering analysis for: {register_request.first_name} {register_request.last_name}")

    # Send asynchronously
    ids = await inngest_client.send(event)

    logger.info(f"Triggered analysis for request_id: {request_id}, Event IDs: {ids}")
    return request_id
