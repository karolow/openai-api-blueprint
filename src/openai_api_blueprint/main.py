from fastapi import FastAPI

app = FastAPI(
    title="OpenAI API Blueprint",
    description="Template for creating OpenAI-compatible APIs.",
    version="0.1.0",
)

@app.get("/health", tags=["Management"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}
