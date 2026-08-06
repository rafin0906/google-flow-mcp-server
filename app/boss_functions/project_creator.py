from typing import Optional, Dict, Any
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright, Page

from app.config import BASE_URL
from app.services import (
    click_new_project,
    select_aspect_ratio,
    save_project_record,
    take_screenshot,
    launch_flow_browser,
)


def create_project(
    ratio: str = "16:9",
    page: Optional[Page] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Boss Function 1: Project Creator
    1. Opens https://labs.google/fx/tools/flow
    2. Clicks 'New project' button
    3. Retrieves the new project URL after redirection
    4. Saves project info into db/projects.json
    5. Clicks the Nano Banana 2 capsule button and selects the target aspect ratio
    6. Updates DB record with ratio selection
    """
    print("\n==========================================")
    print("BOSS FUNCTION 1: PROJECT CREATOR")
    print("==========================================")

    def _execute_creator(active_page: Page) -> Dict[str, Any]:
        print(f"\n[Project Creator] Step 1: Navigating to Google Flow ({BASE_URL})...")
        active_page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120000)
        active_page.wait_for_timeout(3000)
        print(f"[Project Creator] Flow opened. Current URL: {active_page.url}")

        print("\n[Project Creator] Step 2: Clicking 'New project' button...")
        click_new_project(active_page)

        active_page.wait_for_timeout(3000)
        project_url = active_page.url
        print(f"\n[Project Creator] Step 3: New project created successfully!")
        print(f"                  Project Page Link: {project_url}")

        take_screenshot(active_page, "project_creator_new_project.png")

        print("\n[Project Creator] Step 4: Saving project link to DB (db/projects.json)...")
        record = save_project_record(project_url=project_url, ratio=ratio)

        print(f"\n[Project Creator] Step 5 & 6: Selecting Aspect Ratio ({ratio})...")
        selected_ratio = select_aspect_ratio(active_page, ratio=ratio)

        record["ratio"] = selected_ratio
        take_screenshot(active_page, "project_creator_ratio_selected.png")

        print("\n==========================================")
        print("[Project Creator] COMPLETED SUCCESSFULLY!")
        print(f"Project URL: {project_url}")
        print(f"Aspect Ratio: {selected_ratio}")
        print("==========================================\n")
        return record

    if page is not None:
        return _execute_creator(page)
    else:
        with sync_playwright() as p:
            context, active_page = launch_flow_browser(p, headless=headless)
            try:
                result = _execute_creator(active_page)
                try:
                    input("\nProject creation completed. Press ENTER to exit/close Chrome...")
                except (EOFError, KeyboardInterrupt):
                    pass
                return result
            finally:
                context.close()


if __name__ == "__main__":
    create_project()