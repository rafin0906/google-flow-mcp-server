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

PROFILE_DIRECTORY = "Default"
