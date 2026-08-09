"""
MCP Server implementation for Google Flow Automation.
Exposes the 4 Boss Functions as MCP Tools over STDIO.
"""

import os
import sys
import warnings
from typing import Optional, List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Redirect standard built-in print calls to stderr so helper debug prints don't corrupt STDIO JSON-RPC stdout
import builtins
_original_print = builtins.print
def _stderr_print(*args, **kwargs):
    if "file" not in kwargs or kwargs["file"] is None:
        kwargs["file"] = sys.stderr
    _original_print(*args, **kwargs)
builtins.print = _stderr_print

# Suppress runtime warnings that could corrupt STDIO JSON-RPC
warnings.filterwarnings("ignore")

import json
import mcp.types as types
from fastmcp import FastMCP

from app.boss_functions import (
    create_project,
    generate_poster,
    edit_poster,
    change_ratio_and_download,
)

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from app.config import get_public_image_url, SERVER_HOST, MCP_PORT, MCP_TRANSPORT, DOWNLOADS_DIR, PUBLIC_BASE_URL

# Initialize FastMCP Server
mcp = FastMCP("Google Flow MCP Server")


@mcp.custom_route("/downloads/{filename:path}", methods=["GET"])
async def serve_download_image(request: Request):
    """Serves downloaded poster images over HTTP/HTTPS directly from FastMCP."""
    filename = request.path_params.get("filename")
    file_path = DOWNLOADS_DIR / filename
    if file_path.exists():
        return FileResponse(str(file_path))
    return JSONResponse({"error": "File not found"}, status_code=404)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "downloads_dir": str(DOWNLOADS_DIR),
        "public_base_url": PUBLIC_BASE_URL,
    })




def format_mcp_tool_result(result_dict: Dict[str, Any]) -> List[Any]:
    """
    Formats tool result dictionary into lightweight standard MCP content blocks.
    Strips heavy Base64 payload to prevent burning Claude Desktop token limits,
    relying on public_image_url for fast, lightweight rendering.
    """
    result_dict.pop("downloaded_image_b64", None)
    download_path = result_dict.get("downloaded_image_path")

    if download_path and not result_dict.get("public_image_url"):
        result_dict["public_image_url"] = get_public_image_url(download_path)

    public_url = result_dict.get("public_image_url", "")
    status = result_dict.get("status", "completed")
    project_url = result_dict.get("project_url", "")

    # Construct formatted response text
    json_summary = json.dumps(result_dict, indent=2)

    text_parts = [
        f"### 🎨 Poster Output Metadata\n```json\n{json_summary}\n```"
    ]

    if public_url:
        text_parts.append(
            f"\n### 🖼️ Public Poster Image\n"
            f"![Poster Preview]({public_url})\n\n"
            f"🔗 **Public Download Link:** [{public_url}]({public_url})\n"
        )

        # Lightweight HTML Artifact block using HTTPS public URL
        artifact_html = f"""```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Google Flow Poster Viewer</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 24px; max-width: 640px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); text-align: center; }}
    .poster-img {{ width: 100%; height: auto; max-height: 70vh; border-radius: 12px; border: 1px solid #475569; margin-bottom: 20px; object-fit: contain; }}
    .btn-row {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 16px; }}
    .btn {{ background: #3b82f6; color: #ffffff; padding: 12px 24px; border-radius: 8px; font-weight: 600; text-decoration: none; font-size: 14px; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 8px; }}
    .btn:hover {{ background: #2563eb; }}
    .btn-secondary {{ background: #334155; color: #cbd5e1; }}
    .btn-secondary:hover {{ background: #475569; color: #ffffff; }}
    .meta {{ text-align: left; background: #0f172a; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #94a3b8; margin-bottom: 16px; line-height: 1.6; word-break: break-all; }}
  </style>
</head>
<body>
  <div class="card">
    <img src="{public_url}" alt="Generated Poster" class="poster-img" />
    <div class="meta">
      <div><strong>Status:</strong> {status}</div>
      <div><strong>Public URL:</strong> <a href="{public_url}" target="_blank" style="color:#60a5fa;">{public_url}</a></div>
    </div>
    <div class="btn-row">
      <a href="{public_url}" target="_blank" download class="btn">⬇ Download High-Res Poster</a>
      {f'<a href="{project_url}" target="_blank" class="btn btn-secondary">🌐 Open Flow Project</a>' if project_url else ''}
    </div>
  </div>
</body>
</html>
```"""
        text_parts.append(f"\n### 📊 Live Poster Side Panel Artifact\n{artifact_html}")

    return [
        types.TextContent(
            type="text",
            text="\n\n".join(text_parts)
        )
    ]





import asyncio

# Concurrency Mutex Lock: Ensures multiple users/requests queue up sequentially
# without crashing Playwright's persistent Chrome profile lock.
_tool_lock = asyncio.Lock()


async def _run_sync_tool(func, *args, **kwargs):
    """
    Executes a synchronous function containing Playwright sync API calls in a worker thread.
    Initializes a new isolated asyncio event loop in the worker thread so Playwright
    does not detect the main server asyncio event loop.
    """
    def wrapper():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return func(*args, **kwargs)
        finally:
            try:
                new_loop.close()
            except Exception:
                pass

    return await asyncio.to_thread(wrapper)


@mcp.tool()
async def tool_create_project(
    ratio: str = "4:3",
    headless: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Boss Function 1: Creates a new Google Flow project page, saves the project URL to DB (db/projects.json),
    and selects the desired aspect ratio.

    Args:
        ratio: Aspect ratio for the project (options: '16:9', '4:3', '1:1', '3:4', '9:16'). Default: '4:3'.
        headless: Optional boolean override for headless mode. If None, uses HEADLESS from app/config.py.

    Returns:
        Dict containing project_url, ratio, created_at timestamp, and status.
    """
    async with _tool_lock:
        return await _run_sync_tool(create_project, ratio=ratio, headless=headless)


@mcp.tool()
async def tool_generate_poster(
    project_url: Optional[str] = None,
    prompt: Optional[str] = None,
    images_b64: Optional[List[Dict[str, str]]] = None,
    headless: Optional[bool] = None,
) -> List[Any]:
    """
    Boss Function 2: Generates a poster in Google Flow: pastes base64 input images and prompt onto the canvas,
    clicks Send, opens the generated image edit page, records the image_edit_page_url in DB, and downloads 1K output.

    Args:
        project_url: Optional target project URL. If not provided, automatically uses the latest project from DB.
        prompt: Optional custom prompt text. If not provided, uses default FLOW_PROMPT.
        images_b64: Optional list of base64 image payload objects to paste. Format: [{"name": "image.png", "mime": "image/png", "b64": "<base64_string>"}]
        headless: Optional boolean override for headless mode. If None, uses HEADLESS from app/config.py.

    Returns:
        List containing TextContent (metadata + HTML Artifact) and ImageContent.
    """
    async with _tool_lock:
        res = await _run_sync_tool(
            generate_poster,
            project_url=project_url,
            prompt=prompt,
            images_b64=images_b64,
            headless=headless,
        )
        return format_mcp_tool_result(res)


@mcp.tool()
async def tool_edit_poster(
    image_edit_page_url: Optional[str] = None,
    edit_prompt: Optional[str] = None,
    headless: Optional[bool] = None,
) -> List[Any]:
    """
    Boss Function 3: Edits/refines an existing poster image using the image_edit_page_url stored in DB,
    submits the editing prompt, captures the updated image edit URL, and downloads the new variation.

    Args:
        image_edit_page_url: Optional image edit URL. If not provided, uses the latest image_edit_page_url from DB.
        edit_prompt: Optional custom edit prompt. If not provided, uses default FLOW_EDIT_PROMPT.
        headless: Optional boolean override for headless mode. If None, uses HEADLESS from app/config.py.

    Returns:
        List containing TextContent (metadata + HTML Artifact) and ImageContent.
    """
    async with _tool_lock:
        res = await _run_sync_tool(
            edit_poster,
            image_edit_page_url=image_edit_page_url,
            edit_prompt=edit_prompt,
            headless=headless,
        )
        return format_mcp_tool_result(res)


@mcp.tool()
async def tool_poster_ratio_editor(
    edit_url: Optional[str] = None,
    ratio: str = "4:3",
    prompt: Optional[str] = None,
    headless: Optional[bool] = None,
) -> List[Any]:
    """
    Boss Function 4: Opens the latest image edit page from DB (db/projects.json), selects the target model aspect ratio,
    submits the ratio change prompt, captures the updated edit URL, and downloads the output image.

    Args:
        edit_url: Optional image edit URL. If not provided, uses the latest image_edit_page_url from DB.
        ratio: Target aspect ratio (options: '16:9', '4:3', '1:1', '3:4', '9:16'). Default: '4:3'.
        prompt: Optional ratio change prompt. If not provided, uses default FLOW_RATIO_CHANGE_PROMPT.
        headless: Optional boolean override for headless mode. If None, uses HEADLESS from app/config.py.

    Returns:
        List containing TextContent (metadata + HTML Artifact) and ImageContent.
    """
    async with _tool_lock:
        res = await _run_sync_tool(
            change_ratio_and_download,
            edit_url=edit_url,
            ratio=ratio,
            prompt=prompt,
            headless=headless,
        )
        return format_mcp_tool_result(res)



def run_server():
    """
    Runs the FastMCP server.
    Supports both STDIO (default) and HTTP Streamable mode (for web/VPS deployment).
    Set MCP_TRANSPORT=http (or pass argument 'http' / 'sse') to run in HTTP mode.
    """
    transport = MCP_TRANSPORT.lower()
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["http", "--http", "sse", "--sse"]:
        transport = "http"
    elif transport in ["sse", "http"]:
        transport = "http"

    if transport == "http":
        print(f"==================================================")
        print(f" Starting FastMCP Server with HTTP transport")
        print(f" Listening on {SERVER_HOST}:{MCP_PORT}")
        print(f"==================================================")
        mcp.run(transport="http", host=SERVER_HOST, port=MCP_PORT, show_banner=False)
    else:
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    run_server()