import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright, Page

from app.services import (
    paste_images_into_flow,
    enter_prompt_and_send,
    open_latest_generated_image,
    download_generated_image,
    get_compressed_image_b64,
    get_latest_project_record,
    update_project_record,
    take_screenshot,
    launch_flow_browser,
)
from app.config import INPUT_IMAGES_DIR
from app.services.clipboard_handler import get_image_mime, clear_input_images


def generate_poster(
    project_url: Optional[str] = None,
    prompt: Optional[str] = None,
    images_b64: Optional[List[Dict[str, str]]] = None,
    page: Optional[Page] = None,
    headless: Optional[bool] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Boss Function 2: Poster Generator
    1. Opens the recently created project using project_url or fetching from DB
    2. Pastes base64 images payload onto canvas (if images_b64 provided)
    3. Types and submits the prompt
    4. Waits for generation and opens the latest generated image
    5. Retrieves and saves the generated image edit URL (page.url) into db/projects.json
    6. Downloads the generated image, encodes it to base64, and updates DB record
    """
    print("\n==========================================")
    print("BOSS FUNCTION 2: POSTER GENERATOR")
    print("==========================================")

    # 1. Determine target project URL
    if not project_url:
        print("[Poster Generator] Fetching latest created project from DB (db/projects.json)...")
        latest_record = get_latest_project_record(session_id=session_id)
        if not latest_record or not latest_record.get("project_url"):
            raise ValueError(
                "No project URL found in DB. Please run Boss Function 1 (create_project) first."
            )
        project_url = latest_record["project_url"]

    print(f"[Poster Generator] Target Project URL: {project_url}")

    local_images_b64 = []
    has_files = False
    
    session_dir = INPUT_IMAGES_DIR / session_id if session_id else INPUT_IMAGES_DIR
    
    if session_dir.exists():
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                has_files = True
                b64_str = get_compressed_image_b64(file_path, max_dim=1920, quality=95)
                if b64_str:
                    mime_type = get_image_mime(file_path)
                    local_images_b64.append({
                        "name": file_path.name,
                        "mime": mime_type,
                        "b64": b64_str
                    })
                else:
                    print(f"[Poster Generator] Warning: Failed to decode/compress {file_path.name}. Skipping.")

    final_images_b64 = local_images_b64 + (images_b64 or [])

    if has_files and not local_images_b64:
        raise ValueError("All provided input images failed to decode/compress.")

    print(f"[Poster Generator] Total input images to paste: {len(final_images_b64)} image(s)")

    def _execute_generator(active_page: Page) -> Dict[str, Any]:
        # Navigate to project page if not already there
        if active_page.url != project_url:
            print(f"\n[Poster Generator] Step 1: Navigating to project URL: {project_url}...")
            active_page.goto(project_url, wait_until="domcontentloaded", timeout=120000)
            active_page.wait_for_timeout(3000)

        # Step 2: Copy & Paste Images (if provided)
        if final_images_b64:
            print("\n[Poster Generator] Step 2: Pasting base64 input images into Flow...")
            paste_images_into_flow(active_page, final_images_b64)
            take_screenshot(active_page, "poster_generator_images_pasted.png")
        else:
            print("\n[Poster Generator] Step 2: Skipping image paste (no images_b64 provided).")

        # Step 3 & 4: Enter Prompt & Click Send
        print("\n[Poster Generator] Step 3 & 4: Submitting prompt and clicking Send...")
        enter_prompt_and_send(active_page, prompt_text=prompt)
        take_screenshot(active_page, "poster_generator_prompt_submitted.png")

        # Step 5 & 6: Wait & Open Latest Generated Image
        print("\n[Poster Generator] Step 5 & 6: Opening latest generated image on canvas...")
        open_latest_generated_image(active_page)

        # ADDITIONAL TASK: Get image edit page URL
        image_edit_page_url = active_page.url
        print(f"\n[Poster Generator] Step 7: Retrieved Image Edit Page URL!")
        print(f"                  Image Edit Page Link: {image_edit_page_url}")

        print("\n[Poster Generator] Updating DB with Image Edit Page URL...")
        update_project_record(
            project_url=project_url,
            image_edit_page_url=image_edit_page_url,
            status="image_opened",
            session_id=session_id
        )

        take_screenshot(active_page, "poster_generator_image_opened.png")

        # Step 8: Download Generated Image
        print("\n[Poster Generator] Step 8: Downloading generated image...")
        downloaded_file = download_generated_image(active_page)

        # Encode downloaded image to compressed lightweight base64 preview for MCP response (<150KB)
        downloaded_b64 = get_compressed_image_b64(downloaded_file, max_dim=800, quality=75)

        print("\n[Poster Generator] Updating DB with Downloaded Image Path...")
        updated_record = update_project_record(
            project_url=project_url,
            image_edit_page_url=image_edit_page_url,
            downloaded_image_path=downloaded_file,
            status="completed",
            session_id=session_id
        )

        take_screenshot(active_page, "poster_generator_downloaded.png")

        print("\n==========================================")
        print("[Poster Generator] COMPLETED SUCCESSFULLY!")
        print(f"Project URL: {project_url}")
        print(f"Image Edit Page URL: {image_edit_page_url}")
        print(f"Downloaded Image: {downloaded_file}")
        print("==========================================\n")

        result = updated_record or {
            "project_url": project_url,
            "image_edit_page_url": image_edit_page_url,
            "downloaded_image_path": downloaded_file,
            "status": "completed"
        }

        if downloaded_b64:
            result["downloaded_image_b64"] = downloaded_b64

        return result

    try:
        if page is not None:
            return _execute_generator(page)
        else:
            with sync_playwright() as p:
                context, active_page = launch_flow_browser(p, headless=headless)
                try:
                    return _execute_generator(active_page)
                finally:
                    context.close()
    finally:
        if session_id:
            print(f"\n[Poster Generator] Cleaning up input_images directory for session {session_id}...")
        else:
            print("\n[Poster Generator] Cleaning up input_images directory...")
        clear_input_images(session_id)


if __name__ == "__main__":
    generate_poster()