from app.config import SCREENSHOTS_DIR


# ==================================================
# SCREENSHOT CAPTURE SERVICE
# ==================================================

def take_screenshot(
    page,
    filename,
):

    SCREENSHOTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    screenshot_path = (
        SCREENSHOTS_DIR
        / filename
    )

    page.screenshot(
        path=str(
            screenshot_path
        ),
        full_page=True,
    )

    print(
        "\nScreenshot saved:"
    )

    print(
        screenshot_path
    )
