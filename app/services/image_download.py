import time
from pathlib import Path

from app.config import DOWNLOADS_DIR


# ============================================================================
# IMAGE DOWNLOAD & CANVAS SERVICE
# ============================================================================

def open_latest_generated_image(page, timeout=120000):
    """
    Waits for the newly generated image and ensures the edit view / Download button is ready.
    Handles both main project canvas and direct edit page contexts.
    """
    print("\nWaiting for generated image and Download button...")

    download_btn = page.locator('button:has(i:text("download"))')
    if download_btn.count() > 0 and download_btn.first.is_visible():
        print("Edit page is already open and Download button is visible.")
        return page

    image_links = page.locator('a[href*="/edit/"]')
    start_time = time.monotonic()
    image_count = 0

    while True:
        if download_btn.count() > 0 and download_btn.first.is_visible():
            print("Download button appeared on edit page!")
            return page

        try:
            image_count = image_links.count()
        except Exception:
            image_count = 0

        if image_count >= 1:
            break

        elapsed_ms = (time.monotonic() - start_time) * 1000
        if elapsed_ms >= timeout:
            print(f"Timeout reached waiting for image links. Total found: {image_count}")
            break

        page.wait_for_timeout(2000)

    if image_links.count() > 0:
        latest_image_link = image_links.first
        try:
            latest_image_link.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            print("Opening the latest generated image link...")
            latest_image_link.click(timeout=10000)
        except Exception as err:
            print(f"Click on image link skipped/handled: {err}")

    page.wait_for_timeout(2000)
    print("Waiting for Download button on edit page...")
    download_btn.wait_for(state="visible", timeout=timeout)
    print("Edit page loaded and ready.")
    return page



def download_generated_image(
    page,
    download_path=None,
    timeout=120000
):
    """
    Downloads generated image to the designated folder.
    """

    if download_path is None:
        download_path = DOWNLOADS_DIR

    print("\nSearching for the Download button...")

    # Download icon button
    download_button = page.locator(
        'button:has(i:text("download"))'
    )

    download_button.wait_for(
        state="visible",
        timeout=timeout
    )

    print("Clicking the Download button...")

    try:
        download_button.click(timeout=5000)
    except Exception as err:
        print(f"Standard click on Download button intercepted ({err}). Trying Escape and force/JS click...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        try:
            download_button.click(force=True, timeout=5000)
        except Exception:
            download_button.evaluate("(el) => el.click()")

    # Download menu 1K Original size option
    original_size_button = page.locator(
        'button[role="menuitem"]:has-text("1K"):has-text("Original size")'
    )

    original_size_button.wait_for(
        state="visible",
        timeout=timeout
    )

    print("Clicking 1K - Original size...")

    # Wait for download
    with page.expect_download(timeout=timeout) as download_info:
        try:
            original_size_button.click(timeout=5000)
        except Exception:
            try:
                original_size_button.click(force=True, timeout=5000)
            except Exception:
                original_size_button.evaluate("(el) => el.click()")


    download = download_info.value

    # Suggested filename
    suggested_filename = download.suggested_filename

    print(
        f"Download started: {suggested_filename}"
    )

    download_directory = Path(download_path)
    download_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    final_path = (
        download_directory /
        suggested_filename
    )

    # Prevent overwriting an existing file
    if final_path.exists():
        stem = final_path.stem
        suffix = final_path.suffix
        counter = 1
        while final_path.exists():
            final_path = download_directory / f"{stem}_{counter}{suffix}"
            counter += 1

    download.save_as(str(final_path))

    print(
        f"\nDOWNLOAD SUCCESSFUL!"
    )

    print(
        f"Saved to: {final_path}"
    )

    return str(final_path)
