from typing import Optional, Dict, Any, List
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright, Page

from app.services import (
    get_input_images,
    paste_images_into_flow,
    enter_prompt_and_send,
    open_latest_generated_image,
    download_generated_image,
    get_latest_project_record,
    update_project_record,
    take_screenshot,
    launch_flow_browser,
)


def generate_poster(
    project_url: Optional[str] = None,
    prompt: Optional[str] = None,
    image_paths: Optional[List[str]] = None,
    page: Optional[Page] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 2: Poster Generator
    1. Opens the recently created project using project_url or fetching from DB
    2. Copies & pastes images from input_images folder onto canvas
    3. Types and submits the prompt
    4. Waits for generation and opens the latest generated image
    5. ADDITIONAL TASK: Retrieves and saves the generated image edit URL (page.url) into db/projects.json
    6. Downloads the generated image and updates DB record
    """
    print("\n==========================================")
    print("BOSS FUNCTION 2: POSTER GENERATOR")
    print("==========================================")

    # 1. Determine target project URL
    if not project_url:
        print("[Poster Generator] Fetching latest created project from DB (db/projects.json)...")
        latest_record = get_latest_project_record()
        if not latest_record or not latest_record.get("project_url"):
            raise ValueError(
                "No project URL found in DB. Please run Boss Function 1 (create_project) first."
            )
        project_url = latest_record["project_url"]

    print(f"[Poster Generator] Target Project URL: {project_url}")

    # 2. Determine input images
    if image_paths is None:
        image_paths = get_input_images()
    print(f"[Poster Generator] Input images to paste: {image_paths}")

    def _execute_generator(active_page: Page) -> Dict[str, Any]:
        # Navigate to project page if not already there
        if active_page.url != project_url:
            print(f"\n[Poster Generator] Step 1: Navigating to project URL: {project_url}...")
            active_page.goto(project_url, wait_until="domcontentloaded", timeout=120000)
            active_page.wait_for_timeout(3000)

        # Step 2: Copy & Paste Images
        print("\n[Poster Generator] Step 2: Pasting input images into Flow...")
        paste_images_into_flow(active_page, image_paths)
        take_screenshot(active_page, "poster_generator_images_pasted.png")

        # Step 3 & 4: Enter Prompt & Click Send
        print("\n[Poster Generator] Step 3 & 4: Submitting prompt and clicking Send...")
        enter_prompt_and_send(active_page, prompt_text=prompt)
        take_screenshot(active_page, "poster_generator_prompt_submitted.png")

        # Step 5 & 6: Wait & Open Latest Generated Image
        print("\n[Poster Generator] Step 5 & 6: Opening latest generated image on canvas...")
        open_latest_generated_image(active_page)

        # ADDITIONAL TASK: Get image edit page URL
        image_edit_page_url = active_page.url
        print(f"\n[Poster Generator] Step 7 (ADDITIONAL TASK): Retrieved Image Edit Page URL!")
        print(f"                  Image Edit Page Link: {image_edit_page_url}")

        print("\n[Poster Generator] Updating DB with Image Edit Page URL...")
        update_project_record(
            project_url=project_url,
            image_edit_page_url=image_edit_page_url,
            status="image_opened"
        )

        take_screenshot(active_page, "poster_generator_image_opened.png")

        # Step 7: Download Generated Image
        print("\n[Poster Generator] Step 8: Downloading generated image...")
        downloaded_file = download_generated_image(active_page)

        print("\n[Poster Generator] Updating DB with Downloaded Image Path...")
        updated_record = update_project_record(
            project_url=project_url,
            image_edit_page_url=image_edit_page_url,
            downloaded_image_path=downloaded_file,
            status="completed"
        )

        take_screenshot(active_page, "poster_generator_downloaded.png")

        print("\n==========================================")
        print("[Poster Generator] COMPLETED SUCCESSFULLY!")
        print(f"Project URL: {project_url}")
        print(f"Image Edit Page URL: {image_edit_page_url}")
        print(f"Downloaded Image: {downloaded_file}")
        print("==========================================\n")

        return updated_record or {
            "project_url": project_url,
            "image_edit_page_url": image_edit_page_url,
            "downloaded_image_path": downloaded_file,
            "status": "completed"
        }

    if page is not None:
        return _execute_generator(page)
    else:
        with sync_playwright() as p:
            context, active_page = launch_flow_browser(p, headless=headless)
            try:
                result = _execute_generator(active_page)
                try:
                    input("\nPoster generation completed. Press ENTER to exit/close Chrome...")
                except (EOFError, KeyboardInterrupt):
                    pass
                return result


            finally:
                context.close()

if __name__ == "__main__":
    generate_poster()