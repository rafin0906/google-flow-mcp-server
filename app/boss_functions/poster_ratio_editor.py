from typing import Optional, Dict, Any
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright, Page

from app.prompts import FLOW_RATIO_CHANGE_PROMPT
from app.services import (
    select_aspect_ratio,
    enter_edit_prompt_and_send,
    open_latest_generated_image,
    download_generated_image,
    get_latest_project_record,
    update_project_record,
    take_screenshot,
    launch_flow_browser,
)


def change_ratio_and_download(
    edit_url: Optional[str] = None,
    ratio: str = "4:3",
    prompt: Optional[str] = None,
    page: Optional[Page] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 4: Poster Ratio Editor
    1. Opens the image using stored edit page link from DB (db/projects.json)
    2. Clicks the model selector button and selects the desired ratio
    3. Places the ratio changer prompt into the prompt input field
    4. Clicks the Send button
    5. Waits for generation of the new image variation and opens it
    6. Downloads the new image (1K Original size) and updates DB record
    """
    print("\n==========================================")
    print("BOSS FUNCTION 4: POSTER RATIO EDITOR")
    print("==========================================")

    # 1. Determine target edit page URL from DB
    if not edit_url:
        print("[Ratio Selector] Fetching latest image edit URL from DB (db/projects.json)...")
        latest_record = get_latest_project_record()
        if not latest_record or not latest_record.get("image_edit_page_url"):
            raise ValueError(
                "No 'image_edit_page_url' found in DB. Please run Boss Function 2 (generate_poster) first."
            )
        edit_url = latest_record["image_edit_page_url"]

    print(f"[Ratio Selector] Target Edit URL: {edit_url}")
    print(f"[Ratio Selector] Target Aspect Ratio: {ratio}")

    # Determine prompt text
    target_prompt = prompt if prompt is not None else FLOW_RATIO_CHANGE_PROMPT
    print(f"[Ratio Selector] Ratio Changer Prompt: '{target_prompt}'")

    def _execute_ratio_changer(active_page: Page) -> Dict[str, Any]:
        # Step 1: Open stored link
        print(f"\n[Ratio Selector] Step 1: Navigating to image edit page: {edit_url}...")
        active_page.goto(edit_url, wait_until="domcontentloaded", timeout=120000)
        active_page.wait_for_timeout(3000)

        take_screenshot(active_page, "ratio_selector_page_opened.png")

        # Step 2: Click model selector btn & select desired ratio
        print(f"\n[Ratio Selector] Step 2: Clicking model selector button & selecting ratio '{ratio}'...")
        selected_ratio = select_aspect_ratio(active_page, ratio=ratio)
        take_screenshot(active_page, "ratio_selector_ratio_selected.png")

        # Step 3 & 4: Placing prompt & clicking Send
        print(f"\n[Ratio Selector] Step 3 & 4: Entering prompt and clicking Send...")
        enter_edit_prompt_and_send(active_page, prompt_text=target_prompt)
        take_screenshot(active_page, "ratio_selector_prompt_submitted.png")

        # Step 5: Wait for generation & open new image
        print("\n[Ratio Selector] Step 5: Waiting for new image generation and opening it...")
        open_latest_generated_image(active_page)

        new_image_edit_url = active_page.url
        print(f"[Ratio Selector] New Image Edit URL: {new_image_edit_url}")
        take_screenshot(active_page, "ratio_selector_new_image_opened.png")

        # Step 6: Click Download (Original Size)
        print("\n[Ratio Selector] Step 6: Downloading new image (1K Original Size)...")
        downloaded_file = download_generated_image(active_page)

        print("\n[Ratio Selector] Updating DB record...")
        updated_record = update_project_record(
            image_edit_page_url=new_image_edit_url,
            downloaded_image_path=downloaded_file,
            ratio=selected_ratio,
            status="ratio_edited"
        )

        take_screenshot(active_page, "ratio_selector_downloaded.png")

        print("\n==========================================")
        print("[Ratio Selector] COMPLETED SUCCESSFULLY!")
        print(f"Edit URL: {new_image_edit_url}")
        print(f"Aspect Ratio: {selected_ratio}")
        print(f"Downloaded Image: {downloaded_file}")
        print("==========================================\n")

        return updated_record or {
            "image_edit_page_url": new_image_edit_url,
            "ratio": selected_ratio,
            "downloaded_image_path": downloaded_file,
            "status": "ratio_edited"
        }

    if page is not None:
        return _execute_ratio_changer(page)
    else:
        with sync_playwright() as p:
            context, active_page = launch_flow_browser(p, headless=headless)
            try:
                result = _execute_ratio_changer(active_page)
                try:
                    input("\nRatio selection & image generation completed. Press ENTER to exit/close Chrome...")
                except (EOFError, KeyboardInterrupt):
                    pass
                return result
            finally:
                context.close()


if __name__ == "__main__":
    change_ratio_and_download()