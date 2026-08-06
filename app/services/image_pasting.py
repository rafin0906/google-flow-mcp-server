from pathlib import Path
from typing import Union, List
from app.services.clipboard_handler import copy_image_to_clipboard


# ==================================================
# IMAGE PASTING SERVICE
# ==================================================

def paste_images_into_flow(
    page,
    image_paths: Union[List[Path], Path],
):

    if isinstance(image_paths, Path):
        image_paths = [image_paths]

    if not image_paths:
        print("\nNo images provided to paste.")
        return

    print(
        f"\nStarting copy & paste for {len(image_paths)} image(s)..."
    )

    textbox = page.locator(
        "div[role='textbox']"
        "[contenteditable='true']"
    ).last

    textbox.wait_for(
        state="visible",
        timeout=30000,
    )

    print(
        "Flow textbox found."
    )

    total_images = len(image_paths)

    for index, image_path in enumerate(image_paths, start=1):
        print(
            f"\n[{index}/{total_images}] Processing image: {image_path.name}"
        )

        # Copy current image to Windows clipboard
        copy_image_to_clipboard(
            image_path
        )

        textbox.scroll_into_view_if_needed()

        try:
            textbox.click(
                timeout=5000
            )
        except Exception:
            print("Normal click on textbox intercepted, pressing Escape to clear overlays...")
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            textbox.click(
                timeout=15000,
                force=True
            )


        # Ensure editor receives focus
        page.wait_for_timeout(
            1000
        )

        print(
            f"[{index}/{total_images}] Pasting '{image_path.name}' with Ctrl + V..."
        )

        textbox.press(
            "Control+V"
        )

        print(
            f"[{index}/{total_images}] Paste command sent."
        )

        # Pause briefly between consecutive image pastes if more remain
        if index < total_images:
            print(
                "Waiting 3 seconds before copying next image..."
            )
            page.wait_for_timeout(
                3000
            )

    # ==============================================
    # IMPORTANT:
    # Wait 15 seconds BEFORE writing any prompt.
    # ==============================================

    print(
        "\nWaiting 15 seconds "
        "for Flow to process "
        "all pasted image(s)..."
    )

    page.wait_for_timeout(
        15_000
    )

    print(
        "15-second image "
        "processing wait completed."
    )


def paste_image_into_flow(
    page,
    image_path: Path,
):

    paste_images_into_flow(
        page,
        image_path,
    )

