import base64
from pathlib import Path
from typing import Dict, Any, List, Union


def get_image_mime(path: Path) -> str:
    """Returns MIME type based on file extension."""
    ext = path.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    if ext == ".gif":
        return "image/gif"
    return "application/octet-stream"


def prepare_image_payloads(
    image_paths: Union[List[Path], Path]
) -> List[Dict[str, Any]]:
    """
    Reads image file(s) and converts them into Base64 payload dictionary objects
    suitable for in-browser JavaScript DataTransfer clipboard event dispatching.
    """
    if isinstance(image_paths, Path):
        image_paths = [image_paths]

    payloads = []
    for img in image_paths:
        if not img.exists():
            continue
        payloads.append({
            "name": img.name,
            "mime": get_image_mime(img),
            "b64": base64.b64encode(img.read_bytes()).decode("utf-8")
        })
    return payloads

