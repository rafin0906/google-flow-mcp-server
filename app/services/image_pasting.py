from pathlib import Path
from typing import Union, List
from app.services.clipboard_handler import prepare_image_payloads

# ==================================================
# IN-BROWSER IMAGE PASTING SERVICE (CROSS-PLATFORM)
# ==================================================

JS_PASTE_IMAGES = """
([element, images]) => {
    function b64ToBlob(b64Data, contentType) {
        const byteCharacters = atob(b64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: contentType });
    }

    const target = element || document.querySelector("div[role='textbox'][contenteditable='true']") || document.activeElement;
    if (target && target.focus) {
        target.focus();
    }

    const dataTransfer = new DataTransfer();

    for (const img of images) {
        const blob = b64ToBlob(img.b64, img.mime);
        const file = new File([blob], img.name, { type: img.mime });
        dataTransfer.items.add(file);
    }

    const event = new ClipboardEvent("paste", {
        clipboardData: dataTransfer,
        bubbles: true,
        cancelable: true
    });

    if (target) {
        target.dispatchEvent(event);
    }
    const slateEditor = document.querySelector("div[role='textbox'][contenteditable='true']");
    if (slateEditor && slateEditor !== target) {
        slateEditor.dispatchEvent(event);
    }
    if (document.activeElement && document.activeElement !== target && document.activeElement !== slateEditor) {
        document.activeElement.dispatchEvent(event);
    }

    return true;
}
"""


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
        f"\nStarting cross-platform image paste for {len(image_paths)} image(s)..."
    )

    textbox = page.locator(
        "div[role='textbox']"
        "[contenteditable='true']"
    ).last

    textbox.wait_for(
        state="visible",
        timeout=30000,
    )

    print("Flow textbox found.")

    textbox.scroll_into_view_if_needed()

    try:
        textbox.click(timeout=5000)
    except Exception:
        print("Normal click on textbox intercepted, pressing Escape to clear overlays...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        textbox.click(timeout=15000, force=True)

    textbox.focus()
    page.wait_for_timeout(1000)

    # Convert image files to Base64 payloads
    payloads = prepare_image_payloads(image_paths)

    if not payloads:
        print("No valid image files found to paste.")
        return

    print(f"Pasting {len(payloads)} image(s) into Flow via in-browser ClipboardEvent...")

    page.evaluate(JS_PASTE_IMAGES, [textbox.element_handle(), payloads])

    print(f"Pasted {len(payloads)} image(s) successfully.")

    # Wait 15 seconds for Google Flow canvas to process all pasted images
    print(
        "\nWaiting 15 seconds for Flow to process all pasted image(s)..."
    )

    page.wait_for_timeout(15_000)

    print("15-second image processing wait completed.")


def paste_image_into_flow(
    page,
    image_path: Path,
):
    paste_images_into_flow(
        page,
        image_path,
    )


