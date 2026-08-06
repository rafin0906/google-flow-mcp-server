from pathlib import Path
# pyrefly: ignore [missing-import]
from playwright.sync_api import Playwright, BrowserContext, Page
from app.config import USER_DATA_DIR, PROFILE_DIRECTORY


def launch_flow_browser(
    playwright_instance: Playwright,
    headless: bool = False
) -> tuple[BrowserContext, Page]:
    """
    Launches Chrome persistent context with the saved profile.
    Returns (context, page).
    """
    if not USER_DATA_DIR.exists():
        raise FileNotFoundError(
            f"chrome_profile folder was not found:\n{USER_DATA_DIR}"
        )

    if not (USER_DATA_DIR / PROFILE_DIRECTORY).exists():
        raise FileNotFoundError(
            f"Default Chrome profile was not found:\n{USER_DATA_DIR / PROFILE_DIRECTORY}"
        )

    print("\nLaunching Google Chrome (persistent context)...")
    print(f"Profile directory: {USER_DATA_DIR}")

    context = playwright_instance.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        channel="chrome",
        headless=headless,
        accept_downloads=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            f"--profile-directory={PROFILE_DIRECTORY}",
        ],
        viewport={
            "width": 1366,
            "height": 768,
        },
    )

    page = context.pages[0] if context.pages else context.new_page()
    return context, page
