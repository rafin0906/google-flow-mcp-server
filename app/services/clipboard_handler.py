from pathlib import Path
from io import BytesIO
import win32clipboard
# pyrefly: ignore [missing-import]
from PIL import Image


# ==================================================
# WINDOWS CLIPBOARD SERVICE
# ==================================================

def copy_image_to_clipboard(
    image_path: Path,
):

    print(
        "\nCopying image to "
        "Windows clipboard..."
    )

    with Image.open(
        image_path
    ) as image:

        image = image.convert(
            "RGB"
        )

        output = BytesIO()

        image.save(
            output,
            format="BMP",
        )

        bmp_data = (
            output.getvalue()
        )

    # Remove BMP file header
    dib_data = (
        bmp_data[14:]
    )

    win32clipboard.OpenClipboard()

    try:

        win32clipboard.EmptyClipboard()

        win32clipboard.SetClipboardData(
            win32clipboard.CF_DIB,
            dib_data,
        )

    finally:

        win32clipboard.CloseClipboard()

    print(
        "Image copied successfully."
    )
