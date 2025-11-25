from __future__ import annotations

import shutil
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile
from PIL import Image

from config import CARD_MAX_WIDTH, MEDIA_ROOT, NORMAL_MAX_WIDTH

# Validacion de tipo y guardado de archivos en WebP + version reducida para cards


def detect_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    if ext in image_exts:
        return "image"
    if ext in video_exts:
        return "video"
    raise HTTPException(status_code=400, detail="Formato de archivo no permitido")


def resize_image(img: Image.Image, max_width: int) -> Image.Image:
    if img.width <= max_width:
        return img.copy()
    ratio = max_width / img.width
    new_size = (max_width, int(img.height * ratio))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def save_file(file: UploadFile) -> Tuple[str, Optional[str], str, str]:
    media_tipo = detect_media_type(file.filename)
    filename_base = uuid.uuid4().hex

    if media_tipo == "image":
        raw = file.file.read()
        image = Image.open(BytesIO(raw)).convert("RGB")
        normal_img = resize_image(image, NORMAL_MAX_WIDTH)
        card_img = resize_image(image, CARD_MAX_WIDTH)

        normal_name = f"{filename_base}.webp"
        card_name = f"{filename_base}_card.webp"

        normal_img.save(MEDIA_ROOT / normal_name, "WEBP", quality=85, method=6)
        card_img.save(MEDIA_ROOT / card_name, "WEBP", quality=80, method=6)

        return (
            f"/media/{normal_name}",
            f"/media/{card_name}",
            media_tipo,
            file.filename,
        )

    # videos u otros tipos permitidos se guardan tal cual
    ext = Path(file.filename).suffix.lower()
    filename = f"{filename_base}{ext}"
    with (MEDIA_ROOT / filename).open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/media/{filename}", None, media_tipo, file.filename


def remove_media_files(*urls: Optional[str]) -> None:
    """Elimina archivos fisicos asociados a las URLs dadas."""
    for url in urls:
        if not url:
            continue
        filename = Path(url).name
        path = MEDIA_ROOT / filename
        if path.exists():
            path.unlink()
