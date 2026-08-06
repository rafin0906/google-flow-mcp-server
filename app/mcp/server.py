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

# Suppress runtime warnings that could corrupt STDIO JSON-RPC
warnings.filterwarnings("ignore")

# pyrefly: ignore [missing-import]
from fastmcp import FastMCP

from app.boss_functions import (
    create_project,
    generate_poster,
    edit_poster,
    change_ratio_and_download,
)

# Initialize FastMCP Server
mcp = FastMCP("Google Flow MCP Server")


@mcp.tool()
def tool_create_project(
    ratio: str = "4:3",
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 1: Creates a new Google Flow project page, saves the project URL to DB (db/projects.json),
    and selects the desired aspect ratio.

    Args:
        ratio: Aspect ratio for the project (options: '16:9', '4:3', '1:1', '3:4', '9:16'). Default: '4:3'.
        headless: Whether to run Chrome browser in headless mode. Default: False.

    Returns:
        Dict containing project_url, ratio, created_at timestamp, and status.
    """
    return create_project(ratio=ratio, headless=headless)


@mcp.tool()
def tool_generate_poster(
    project_url: Optional[str] = None,
    prompt: Optional[str] = None,
    image_paths: Optional[List[str]] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 2: Generates a poster in Google Flow: pastes input images and prompt onto the canvas,
    clicks Send, opens the generated image edit page, records the image_edit_page_url in DB, and downloads 1K output.

    Args:
        project_url: Optional target project URL. If not provided, automatically uses the latest project from DB.
        prompt: Optional custom prompt text. If not provided, uses default FLOW_PROMPT.
        image_paths: Optional list of image file paths to paste. If not provided, uses images from input_images/.
        headless: Whether to run Chrome browser in headless mode. Default: False.

    Returns:
        Dict containing project_url, image_edit_page_url, downloaded_image_path, and status.
    """
    return generate_poster(
        project_url=project_url,
        prompt=prompt,
        image_paths=image_paths,
        headless=headless,
    )


@mcp.tool()
def tool_edit_poster(
    image_edit_page_url: Optional[str] = None,
    edit_prompt: Optional[str] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 3: Edits/refines an existing poster image using the image_edit_page_url stored in DB,
    submits the editing prompt, captures the updated image edit URL, and downloads the new variation.

    Args:
        image_edit_page_url: Optional image edit URL. If not provided, uses the latest image_edit_page_url from DB.
        edit_prompt: Optional custom edit prompt. If not provided, uses default FLOW_EDIT_PROMPT.
        headless: Whether to run Chrome browser in headless mode. Default: False.

    Returns:
        Dict containing original edit URL, new image_edit_page_url, downloaded_image_path, and status.
    """
    return edit_poster(
        image_edit_page_url=image_edit_page_url,
        edit_prompt=edit_prompt,
        headless=headless,
    )


@mcp.tool()
def tool_poster_ratio_editor(
    edit_url: Optional[str] = None,
    ratio: str = "4:3",
    prompt: Optional[str] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 4: Opens the latest image edit page from DB (db/projects.json), selects the target model aspect ratio,
    submits the ratio change prompt, captures the updated edit URL, and downloads the output image.

    Args:
        edit_url: Optional image edit URL. If not provided, uses the latest image_edit_page_url from DB.
        ratio: Target aspect ratio (options: '16:9', '4:3', '1:1', '3:4', '9:16'). Default: '4:3'.
        prompt: Optional ratio change prompt. If not provided, uses default FLOW_RATIO_CHANGE_PROMPT.
        headless: Whether to run Chrome browser in headless mode. Default: False.

    Returns:
        Dict containing edit URL, selected ratio, downloaded_image_path, and status.
    """
    return change_ratio_and_download(
        edit_url=edit_url,
        ratio=ratio,
        prompt=prompt,
        headless=headless,
    )


def run_server():
    """Runs the FastMCP server via STDIO."""
    # Redirect standard print output to stderr so stdout is purely reserved for FastMCP JSON-RPC protocol
    sys.stdout = sys.stderr
    mcp.run()


if __name__ == "__main__":
    run_server()
