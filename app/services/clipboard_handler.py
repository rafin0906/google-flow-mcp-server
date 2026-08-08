import base64
from pathlib import Path
from typing import Dict, Any, List, Union, Optional


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


def prepare_image_payloads_from_b64(
    images_b64: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Validates and cleans Base64 image payloads passed directly into memory.
    Strips data URL prefixes (e.g. 'data:image/png;base64,') if present.
    Returns payloads formatted for in-browser DataTransfer paste dispatch.
    """
    if not images_b64:
        return []

    payloads = []
    for idx, img in enumerate(images_b64):
        if not isinstance(img, dict):
            continue

        b64_data = img.get("b64", "")
        if not b64_data:
            continue

        # Strip Data URL prefix if present (e.g. data:image/png;base64,...)
        if "," in b64_data and b64_data.strip().startswith("data:"):
            b64_data = b64_data.split(",", 1)[1]

        b64_data = b64_data.strip()

        name = img.get("name") or f"input_image_{idx + 1}.png"
        mime = img.get("mime") or "image/png"

        payloads.append({
            "name": name,
            "mime": mime,
            "b64": b64_data,
        })
    return payloads


def get_compressed_image_b64(
    file_path: Union[str, Path],
    max_dim: int = 800,
    quality: int = 75,
) -> Optional[str]:
    """
    Compresses an image file into a lightweight Base64 JPEG preview string (typically ~80-150KB)
    to safely fit within MCP tool response size limits (e.g. Claude Desktop's 1MB ceiling).
    """
    if not file_path:
        return None

    path = Path(file_path)
    if not path.exists():
        return None

    try:
        from PIL import Image
        import io

        with Image.open(path) as img:
            img.thumbnail((max_dim, max_dim))
            if img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Warning: Could not compress image to base64: {e}")
        return None



