# storage.py
import os
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

IMAGES_DIR = Path(os.getenv("IMAGES_DIR", "./uploaded_images"))
THUMBNAIL_DIR = IMAGES_DIR / "thumbs"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

def _safe_filename(filename: str) -> str:
    # basic sanitization - can use werkzeug.utils.secure_filename if available
    return "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")).rstrip()

def save_image_bytes(file_bytes: bytes, original_filename: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    safe = _safe_filename(original_filename)
    dest_name = f"{ts}_{safe}"
    dest = IMAGES_DIR / dest_name
    with open(dest, "wb") as f:
        f.write(file_bytes)
    return str(dest.resolve())

def create_thumbnail_from_bytes(file_bytes: bytes,original_filename: str, size=(128,128)) -> str:
    img = Image.open(BytesIO(file_bytes)).convert("RGB")
    img.thumbnail(size)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    thumb_name = f"thumb_{ts}.jpg"
    dest = THUMBNAIL_DIR / thumb_name
    img.save(dest, format="JPEG", quality=85)
    return str(dest.resolve())
