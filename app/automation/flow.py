# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

from app.services import launch_flow_browser
from app.boss_functions import create_project, generate_poster


def run_flow(
    ratio: str = "4:3",
    headless: bool = False,
):
    """
    Main Orchestrator using Boss Function 1 (Project Creator)
    and Boss Function 2 (Poster Generator).
    """
    if headless:
        print("\nWARNING: Clipboard paste is more reliable with headless=False.")

    with sync_playwright() as p:
        context, page = launch_flow_browser(p, headless=headless)

        try:
            # Boss Function 1: Create Project & Select Ratio
            project_data = create_project(ratio=ratio, page=page)
            project_url = project_data["project_url"]

            # Boss Function 2: Generate Poster & Download
            poster_data = generate_poster(project_url=project_url, page=page)

            print("\n==========================================")
            print("AUTOMATION FLOW COMPLETE")
            print("==========================================")
            print(f"Project URL: {poster_data.get('project_url')}")
            print(f"Image Edit Page URL: {poster_data.get('image_edit_page_url')}")
            print(f"Downloaded Image Path: {poster_data.get('downloaded_image_path')}")
            print("==========================================\n")
        finally:
            context.close()


