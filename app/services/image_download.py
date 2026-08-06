import time
from pathlib import Path

from app.config import DOWNLOADS_DIR


# ============================================================================
# IMAGE DOWNLOAD & CANVAS SERVICE
# ============================================================================

def open_latest_generated_image(page, timeout=120000):
    """
    Waits until total image links on canvas >= 2 (Source image + newly generated image).
    Then selects and opens the last (newest generated) image link.
    """

    print("\nWaiting for newly generated image on canvas (waiting until total images >= 2)...")

    image_links = page.locator('a[href*="/edit/"]')

    start_time = time.monotonic()
    image_count = 0

    # Poll until at least 2 image links appear
    while True:
        try:
            image_count = image_links.count()
        except Exception:
            image_count = 0

        if image_count >= 2:
            print(f"Newly generated image detected! Total images on canvas: {image_count}")
            break

        elapsed_ms = (time.monotonic() - start_time) * 1000
        if elapsed_ms >= timeout:
            print(f"Timeout reached. Total images currently found: {image_count}")
            break

        page.wait_for_timeout(2000)

    if image_count >= 2:
        # Google Flow displays the newest generated image on the leftmost side (first in DOM)
        latest_image_link = image_links.first
    else:
        print("Fallback: Searching all available generated image links...")
        alt_images = page.locator('img[alt="Generated image"]')
        if alt_images.count() > 0:
            latest_image_link = alt_images.first.locator("xpath=ancestor::a[1]")
        elif image_links.count() > 0:
            latest_image_link = image_links.first
        else:
            raise RuntimeError("No generated image was found on the canvas.")

    latest_image_link.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    print("Opening the latest generated image...")

    latest_image_link.click(timeout=30000)

    page.wait_for_timeout(3000)

    print("Waiting for Download button on edit page...")
    download_button = page.locator('button:has(i:text("download"))')
    download_button.wait_for(state="visible", timeout=timeout)

    print("Edit page loaded and ready.")
    return latest_image_link


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

    download_button.click()

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
        original_size_button.click()

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
