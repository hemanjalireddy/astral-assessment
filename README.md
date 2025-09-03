# Astral Assessment - AI Business Intelligence Pipeline

A FastAPI application that automatically extracts business intelligence from company websites and LinkedIn profiles for prospect research.

## Quick Start

### 1. Install Dependencies

```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -
```
# Install dependencies
```bash
poetry install
```
### 2. Set Up Environment
```bash
cp .env.templ .env
```
#### Add your API keys to .env:
```bash
FIRECRAWL_API_KEY=fc-your_firecrawl_key_here
INNGEST_EVENT_KEY=evt_your_inngest_key_here
INNGEST_SIGNING_KEY=signkey_your_inngest_key_here
```

### 3. Running Astral Assessment with Inngest

#### 1.Start the Inngest Dev Server
Run this in your project root:

```bash
npx inngest-cli@latest dev
```
This boots the local Inngest runtime, which will capture and run events from your FastAPI app.

#### 2.Run FastAPI with Inngest Dev Mode

In a new terminal window, set the Inngest dev flag and start your app:

```bash
$env:INNGEST_DEV=1
uvicorn main:app --reload
```

INNGEST_DEV=1 ensures that Inngest connects to your local dev server instead of production.

uvicorn serves your FastAPI app at http://localhost:8000.

#### 3.Register Your App with Inngest

Once both are running:

Go to http://localhost:8288
 (Inngest Dev UI).

You’ll see your FastAPI app show up as a connected application.

It will automatically register the process-registration function defined in your code.

#### 4.Trigger the Function

You can now test it in two ways:

Option A: Using Inngest Dev UI

    Open the Inngest Dev UI.

    Select the process-registration function.

    Manually send an event with this JSON payload:

    ```json
    {
        "data": {
            "request_id": "abc-123-def-456",
            "timestamp": "2025-09-03T14:30:22.123456",
            "input_data": {
            "first_name": "Sarah",
            "last_name": "Chen",
            "company_website": "https://www.linear.app",
            "linkedin": null
                    }
        }
    }
    ```

Option B: Programmatically

Your trigger_analysis() helper in code already sends an event. You can call that from a test route or Python REPL.


#### 5.View Results

Logs will stream in your terminal (uvicorn + npx inngest-cli dev).

Processed output JSON will be saved in the /outputs directory.

```json

{
  "discovered_urls": [
    "https://linear.app/docs/security",
    "https://linear.app/developers",
    "https://linear.app/changelog/page/21"
  ],
  "errors": [],
  "filtered_urls": [
    "https://linear.app/docs/security",
    "https://linear.app/developers",
    "https://linear.app/changelog/page/21"
  ],
  "filtering_logic": "Filtered 7 URLs to 7 high-value URLs",
  "scraped_content": {
    "https://linear.app/changelog/2019-10-14-improved-comments": "..."
  }
}
```

With this setup, every time you POST /register or send a registration.submitted event, Inngest will queue and execute your background function.

What /register endpoint does:
- Validates the request (requires at least website OR LinkedIn)
- Discovers URLs from the company website using Firecrawl
- Filters to find the most valuable pages (about, team, services, etc.)
- Scrapes content from top 7 URLs in markdown format
- Generates analysis saved as JSON in the /outputs directory

Example Output
- Check the /outputs directory for files like analysis_20250903_143022.json:

```json
{
  "request_id": "abc-123-def",
  "timestamp": "2025-09-03T14:30:22Z",
  "input_data": {
    "first_name": "Sarah",
    "last_name": "Chen",
    "company_website": "https://www.linear.app"
  },
  "linkedin_analysis": {
    "status": "not_implemented",
    "implementation_plan": "Comprehensive strategy for LinkedIn integration..."
  },
  "website_analysis": {
    "discovered_urls": ["https://linear.app/about", "https://linear.app/team", ...],
    "filtered_urls": ["top 7 most valuable URLs"],
    "scraped_content": {
      "https://linear.app/about": "# About Linear\nLinear is built for speed..."
    }
  }
}
```

### LinkedIn Implementation Plan

The app includes a comprehensive research-based implementation plan for LinkedIn profile extraction:

- Recommended Solution: Proxycurl API ($0.001 per profile)
- Alternative Approaches: ScrapFly + AI processing, PhantomBuster
- Integration Timeline: 4 hours estimated
- Cost Analysis: $1/month for 1000 profiles

![alt text](image.png)

