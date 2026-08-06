import time
import pyperclip
import json
from pathlib import Path

from app.config import (
    TEXTBOX_SELECTOR,
    SEND_BUTTON_SELECTOR,
)
from app.services.image_download import (
    open_latest_generated_image,
    download_generated_image
)

def run_poster_editor(page, db_json_path: Path, edit_prompt: str) -> str:
    print(f"\n[Member 3] Reading database: {db_json_path}")
    
    # 1. Read the database for the image_edit_link
    try:
        with open(db_json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            edit_url = data.get("image_edit_link")
            
        if not edit_url:
            raise ValueError("No 'image_edit_link' found in the JSON database.")
    except Exception as error:
        raise RuntimeError(f"Database read failed: {error}")

    # 2. Navigate to the edit page
    print(f"[Member 3] Navigating to edit URL: {edit_url}")
    page.goto(edit_url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(5000)

    # 3. Locate Textbox and Paste Prompt
    print("\n[Member 3] Locating prompt input field...")
    textbox = page.locator(TEXTBOX_SELECTOR).last
    textbox.wait_for(state="visible", timeout=30000)
    textbox.scroll_into_view_if_needed()
    textbox.click(timeout=15000)
    page.wait_for_timeout(1000)

    print("[Member 3] Copying editing prompt to clipboard...")
    pyperclip.copy(edit_prompt)

    print("[Member 3] Pasting editing prompt into Flow...")
    textbox.press("Control+V")
    page.wait_for_timeout(3000)

    # 4. Click Send
    print("[Member 3] Locating Send button...")
    send_button = page.locator(SEND_BUTTON_SELECTOR).last
    send_button.wait_for(state="visible", timeout=30000)

    send_timeout_ms = 30000
    start_time = time.monotonic()
    send_enabled = False

    while True:
        aria_disabled = send_button.get_attribute("aria-disabled")
        if aria_disabled != "true":
            send_enabled = True
            break
        if (time.monotonic() - start_time) * 1000 >= send_timeout_ms:
            break
        page.wait_for_timeout(500)

    if not send_enabled:
        raise RuntimeError("[Member 3] Send button remained disabled.")

    print("\n[Member 3] Clicking Send...")
    send_button.click(timeout=15000, no_wait_after=True)
    page.wait_for_timeout(3000)

    # 5. Wait for Generation and Select New Image
    print("\n[Member 3] Waiting for Flow to generate the new image variation...")
    open_latest_generated_image(page)

    # 6. Download Final Output
    print("\n[Member 3] Generation complete. Initiating download...")
    final_saved_path = download_generated_image(page)
    
    return final_saved_path