from typing import Optional, Dict, Any
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright, Page

from app.prompts import FLOW_EDIT_PROMPT
from app.services import (
    enter_edit_prompt_and_send,
    open_latest_generated_image,
    download_generated_image,
    get_latest_project_record,
    update_project_record,
    take_screenshot,
    launch_flow_browser,
)


def edit_poster(
    image_edit_page_url: Optional[str] = None,
    edit_prompt: Optional[str] = None,
    page: Optional[Page] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 3: Poster Editor
    1. Opens an existing image edit page URL (fetched from db/projects.json if not provided)
    2. Submits an editing prompt to refine/upgrade the poster
    3. Waits for image generation and opens the new variation on canvas
    4. Retrieves and updates the new image edit URL in db/projects.json
    5. Downloads the edited image and updates DB record
    """
    print("\n==========================================")
    print("BOSS FUNCTION 3: POSTER EDITOR")
    print("==========================================")

    # 1. Determine target image edit URL
    if not image_edit_page_url:
        print("[Poster Editor] Fetching latest 'image_edit_page_url' from DB (db/projects.json)...")
        latest_record = get_latest_project_record()
        if not latest_record or not latest_record.get("image_edit_page_url"):
            raise ValueError(
                "No 'image_edit_page_url' found in DB. Please run Boss Function 2 (generate_poster) first."
            )
        image_edit_page_url = latest_record["image_edit_page_url"]

    print(f"[Poster Editor] Target Image Edit Page URL: {image_edit_page_url}")

    target_prompt = edit_prompt if edit_prompt is not None else FLOW_EDIT_PROMPT

    def _execute_editor(active_page: Page) -> Dict[str, Any]:
        # Step 1: Navigate to the image edit page
        print(f"\n[Poster Editor] Step 1: Navigating to image edit URL: {image_edit_page_url}...")
        active_page.goto(image_edit_page_url, wait_until="domcontentloaded", timeout=120000)
        
        # Wait 2-3 seconds after opening image edit page URL
        print("[Poster Editor] Waiting 3 seconds after edit page loads...")
        active_page.wait_for_timeout(3000)

        # Step 2: Enter Edit Prompt & Click Send (Fast, immediate click)
        print("\n[Poster Editor] Step 2: Submitting edit prompt and clicking Send...")
        enter_edit_prompt_and_send(active_page, prompt_text=target_prompt)
        take_screenshot(active_page, "poster_editor_prompt_submitted.png")

        # Step 3: Wait & Open Latest Generated Variation
        print("\n[Poster Editor] Step 3: Opening newly generated image variation on canvas...")
        open_latest_generated_image(active_page)

        # Step 4: Get updated image edit page URL
        new_image_edit_page_url = active_page.url
        print(f"\n[Poster Editor] Step 4: Retrieved New Image Edit Page URL!")
        print(f"                  New Image Edit Page Link: {new_image_edit_page_url}")

        print("\n[Poster Editor] Updating DB with new Image Edit Page URL...")
        update_project_record(
            image_edit_page_url=new_image_edit_page_url,
            status="image_edited"
        )
        take_screenshot(active_page, "poster_editor_image_opened.png")

        # Step 5: Download Edited Image
        print("\n[Poster Editor] Step 5: Downloading edited image...")
        downloaded_file = download_generated_image(active_page)

        print("\n[Poster Editor] Updating DB with Downloaded Image Path...")
        updated_record = update_project_record(
            image_edit_page_url=new_image_edit_page_url,
            downloaded_image_path=downloaded_file,
            status="edit_completed"
        )
        take_screenshot(active_page, "poster_editor_downloaded.png")

        print("\n==========================================")
        print("[Poster Editor] COMPLETED SUCCESSFULLY!")
        print(f"Original Edit URL: {image_edit_page_url}")
        print(f"New Image Edit Page URL: {new_image_edit_page_url}")
        print(f"Downloaded Image: {downloaded_file}")
        print("==========================================\n")

        return updated_record or {
            "image_edit_page_url": new_image_edit_page_url,
            "downloaded_image_path": downloaded_file,
            "status": "edit_completed"
        }

    if page is not None:
        return _execute_editor(page)
    else:
        with sync_playwright() as p:
            context, active_page = launch_flow_browser(p, headless=headless)
            try:
                return _execute_editor(active_page)
            finally:
                context.close()



if __name__ == "__main__":
    edit_poster()
