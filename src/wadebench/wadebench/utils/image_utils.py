from pathlib import Path
import base64
import mimetypes
from PIL import Image


def image_to_data_url(image_path: str | Path) -> str:
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"

    b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def create_vertical_tiles(
    image_path: str | Path,
    output_dir: str | Path,
    tile_height: int = 1400,
    overlap: int = 180,
    max_width: int = 800,
    max_tiles: int = 12,
) -> list[Path]:
    """
    Split one full-page screenshot into readable vertical tiles.

    B3 still uses only screenshot evidence.
    No OCR, no HTML, no DOM.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path).convert("RGB")

    # Resize very wide screenshots while preserving aspect ratio.
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height))

    tiles = []
    y = 0
    tile_idx = 1

    while y < img.height and tile_idx <= max_tiles:
        bottom = min(y + tile_height, img.height)
        tile = img.crop((0, y, img.width, bottom))

        tile_path = output_dir / f"tile_{tile_idx:02d}.png"
        tile.save(tile_path, optimize=True)

        tiles.append(tile_path)

        if bottom >= img.height:
            break

        y = bottom - overlap
        tile_idx += 1

    return tiles
