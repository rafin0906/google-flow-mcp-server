# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

from app.config import (
    BASE_URL,
    USER_DATA_DIR,
    PROFILE_DIRECTORY,
)
from app.services import (
    click_new_project,
    get_input_images,
    paste_images_into_flow,
    enter_prompt_and_send,
    open_latest_generated_image,
    download_generated_image,
    take_screenshot,
)



# ==================================================
# MAIN AUTOMATION ORCHESTRATOR
# ==================================================

def run_flow(
    headless=False,
):

    # Clipboard paste works best
    # with visible Chrome
    if headless:

        print(
            "\nWARNING:"
        )

        print(
            "Clipboard paste is more "
            "reliable with "
            "headless=False."
        )

    # Check Chrome profile
    if not USER_DATA_DIR.exists():

        raise FileNotFoundError(
            "chrome_profile folder "
            "was not found:\n"
            f"{USER_DATA_DIR}"
        )

    if not (
        USER_DATA_DIR
        / PROFILE_DIRECTORY
    ).exists():

        raise FileNotFoundError(
            "Default Chrome profile "
            "was not found:\n"
            f"{USER_DATA_DIR / PROFILE_DIRECTORY}"
        )

    # Find all input images
    image_paths = (
        get_input_images()
    )

    print(
        "\nLaunching "
        "Google Chrome..."
    )

    print(
        "Profile directory:"
    )

    print(
        USER_DATA_DIR
    )

    with sync_playwright() as p:

        context = (
            p.chromium
            .launch_persistent_context(

                user_data_dir=str(
                    USER_DATA_DIR
                ),

                channel="chrome",

                headless=headless,

                accept_downloads=True,

                args=[
                    "--disable-blink-features="
                    "AutomationControlled",

                    f"--profile-directory="
                    f"{PROFILE_DIRECTORY}",
                ],

                viewport={
                    "width": 1366,
                    "height": 768,
                },
            )
        )

        # Use existing Chrome page
        if context.pages:

            page = (
                context.pages[0]
            )

        else:

            page = (
                context.new_page()
            )

        print(
            "\nOpening Google Flow..."
        )

        page.goto(
            BASE_URL,
            wait_until=(
                "domcontentloaded"
            ),
            timeout=120000,
        )

        print(
            "Google Flow opened."
        )

        print(
            "Current URL:"
        )

        print(
            page.url
        )

        # Wait for Flow UI
        page.wait_for_timeout(
            3000
        )

        # ==========================================
        # STEP 1:
        # CREATE NEW PROJECT
        # ==========================================

        click_new_project(
            page
        )

        take_screenshot(
            page,
            "flow_project_created.png",
        )

        # ==========================================
        # STEP 2:
        # PASTE IMAGES
        # ==========================================

        paste_images_into_flow(
            page,
            image_paths,
        )

        take_screenshot(
            page,
            "flow_image_processed.png",
        )

        # ==========================================
        # STEP 3:
        # TYPE PROMPT AND SEND
        # ==========================================

        enter_prompt_and_send(
            page,
        )

        # ==========================================
        # STEP 4:
        # OPEN LATEST GENERATED IMAGE
        # ==========================================

        open_latest_generated_image(
            page
        )

        # ==========================================
        # STEP 5:
        # DOWNLOAD GENERATED IMAGE
        # ==========================================

        downloaded_file = (
            download_generated_image(
                page
            )
        )

        print(
            "\nFinal downloaded file:"
        )

        print(
            downloaded_file
        )

        take_screenshot(
            page,
            "flow_prompt_submitted.png",
        )

        # Keep browser open
        input(
            "\nAutomation completed.\n"
            "Press ENTER to close "
            "Chrome..."
        )

        context.close()
