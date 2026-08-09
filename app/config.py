from pathlib import Path

# ==================================================
# CONFIGURATION
# ==================================================

BASE_URL = "https://labs.google/fx/tools/flow"

TEXTBOX_SELECTOR = (
    "div[role='textbox']"
    "[contenteditable='true']"
    "[data-slate-editor='true']"
)

SEND_BUTTON_SELECTOR = (
    "button:has("
    "i:text-is('arrow_forward')"
    ")"
)

PROMPT_END_MARKER = (
    "AUTOMATION_PROMPT_COMPLETE_9F3A"
)

# ==========================================
# GENERATED IMAGE / DOWNLOAD SELECTORS
# ==========================================

GENERATED_IMAGE_SELECTOR = (
    "img[alt='Generated image']"
)

DOWNLOAD_BUTTON_SELECTOR = (
    "button:has("
    "i:text-is('download')"
    ")"
)

ORIGINAL_1K_SELECTOR = (
    "button[role='menuitem']"
    ":has-text('Original size')"
)

# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_DIR = Path(
    __file__
).resolve().parent.parent

USER_DATA_DIR = (
    PROJECT_DIR
    / "chrome_profile"
)

INPUT_IMAGES_DIR = (
    PROJECT_DIR
    / "input_images"
)

DOWNLOADS_DIR = (
    PROJECT_DIR
    / "downloads"
)

SCREENSHOTS_DIR = (
    PROJECT_DIR
    / "screenshots"
)

DB_DIR = (
    PROJECT_DIR
    / "db"
)

DB_FILE = (
    DB_DIR
    / "projects.json"
)

PROFILE_DIRECTORY = "Default"

# Global Browser Headless Setting (Set True for VPS/Headless execution, False for GUI mode)
HEADLESS = True

# ==================================================
# PUBLIC MEDIA SERVER CONFIGURATION (VPS / REMOTE)
# ==================================================
import os

try:
    from dotenv import load_dotenv
    _env_file = PROJECT_DIR / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
    else:
        load_dotenv()
except ImportError:
    pass

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")


import urllib.parse

def get_public_image_url(image_path: os.PathLike | str | None) -> str | None:
    """
    Generates a public URL for a downloaded image file.
    Example: /path/to/downloads/poster_123.jpeg -> https://your-domain.ngrok-free.dev/downloads/poster_123.jpeg
    """
    if not image_path:
        return None
    path = Path(image_path)
    base_url = os.getenv("PUBLIC_BASE_URL", PUBLIC_BASE_URL).rstrip("/")
    encoded_filename = urllib.parse.quote(path.name)
    return f"{base_url}/downloads/{encoded_filename}"




