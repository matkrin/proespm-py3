from pathlib import Path
from PIL import Image
import base64
import io

FASTSPM_SCREENSHOT_EXTENSIONS = ("jpg", "jpeg")


def read_corresponding_image(filepath: str, rotate: bool) -> str:
    base_path = Path(filepath).with_suffix("")

    for ext in FASTSPM_SCREENSHOT_EXTENSIONS:
        path = base_path.with_suffix(f".{ext}")
        if path.exists():
            image_path = path
            image_extension = ext
            break
    else:
        raise FileNotFoundError(
            f"No JPEG image found next to the .h5 file '{filepath}'"
        )

    with Image.open(image_path) as img:
        if rotate:
            img = img.rotate(90, expand=True)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

        return f"data:image/{image_extension};base64,{encoded}"
