from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from agent.agent_openai import oai_client
from agent.agent_openai.agent_html import Agent
from agent.schema import UIContext
from agent.logging_utils import setup_logging

setup_logging()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for the frontend
static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

# Serve html_report.html - path should match tools.py location
# tools.py writes to: project_root/temp/reports/
reports_dir = Path(__file__).parent.parent / "temp" / "reports"

@app.get("/temp/html_report.html")
def serve_html_report(user_id: str | None = None):
    from fastapi.responses import FileResponse
    
    filename = f"html_report_{user_id}.html" if user_id else "html_report.html"
    target_path = reports_dir / filename
    
    # Disable cache to ensure always returning the latest file
    if target_path.exists():
        return FileResponse(
            target_path,
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    else:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content="<html><body><h2>No report yet</h2><p>Please chat with AI to generate a report first</p></body></html>",
            status_code=200
        )


@app.get("/")
def root():
    return "visit /docs for APIs"


@app.get("/health")
def health():
    return 200


@app.post("/trigger")
async def trigger(input: UIContext):

    agent = Agent(client=oai_client)
    response_generator = agent.trigger(input)
    return StreamingResponse(
        response_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
