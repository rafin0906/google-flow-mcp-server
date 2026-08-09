"""
FastAPI Public Media Server for Google Flow MCP Server.
Serves downloaded poster images over HTTP/HTTPS for remote VPS, Claude Mobile, Web, Desktop, and n8n.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import DOWNLOADS_DIR, SERVER_HOST, SERVER_PORT, PUBLIC_BASE_URL

# Ensure downloads directory exists
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Google Flow Public Media Server",
    description="Lightweight public image asset endpoint for Google Flow downloaded posters.",
    version="1.0.0",
)

# Mount ONLY the downloads directory for serving generated output images
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "downloads_dir": str(DOWNLOADS_DIR),
        "public_base_url": PUBLIC_BASE_URL,
    }


def main():
    print(f"==================================================")
    print(f" Starting Public Media Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f" Serving /downloads from: {DOWNLOADS_DIR}")
    print(f" Base Public URL: {PUBLIC_BASE_URL}")
    print(f"==================================================")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)


if __name__ == "__main__":
    main()
