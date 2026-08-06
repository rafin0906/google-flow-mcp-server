from pathlib import Path
from app.config import INPUT_IMAGES_DIR


# ==================================================
# INPUT IMAGE SELECTOR SERVICE
# ==================================================

def get_input_images() -> list[Path]:

    if not INPUT_IMAGES_DIR.exists():

        raise FileNotFoundError(
            "input_images folder was not found:\n"
            f"{INPUT_IMAGES_DIR}"
        )

    supported_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
    }

    image_files = [
        file
        for file
        in INPUT_IMAGES_DIR.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in supported_extensions
        )
    ]

    if not image_files:

        raise FileNotFoundError(
            "No supported image was found inside:\n"
            f"{INPUT_IMAGES_DIR}"
        )

    image_files.sort(
        key=lambda file: (
            file.stat().st_mtime
        )
    )

    print(
        f"\nFound {len(image_files)} input image(s):"
    )

    for img in image_files:
        print(
            f"  - {img.name}"
        )

    return image_files


def get_latest_image() -> Path:

    images = get_input_images()

    latest_image = images[-1]

    print(
        "\nSelected newest image:"
    )

    print(
        latest_image
    )

    return latest_image

