from pathlib import Path
from PIL import Image
import base64
import io

from proespm.measurement import Measurement

class FastSPMMeasurement(Measurement):
    """Parent Class for FastSPMMeasurements.

    Args:
        filepath (str): Full path to the .h5 file
    """

    def __init__(self, filepath: str) -> None:
        self.par = read_corresponding_par_file(filepath)


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
    

def read_corresponding_par_file(filepath: str) -> dict | None:
    par_file_path = Path(filepath).with_suffix(".par")
    
    if not par_file_path.exists():
        return None
    else:
        with open(par_file_path) as input:
            lines = input.read().split("\n")
            output = dict({
                'E_WE_V': 'UNDEFINED',
                'I_WE_A': 'UNDEFINED',
                'U_Tun_res_V': 'UNDEFINED',
                'I_Tip_A': 'UNDEFINED',
                'U_Tip_V': 'UNDEFINED'
            })

            for line in lines:
                pair = line.split()

                if len(pair) > 1:
                    unit = " A" if "A" in pair[0] else " V"
                    output[pair[0]] = pair[1] + unit

            return output

"""
SYNTAX:

identifier, value := # ~(WHITESPACE)

value_pair := identifier WHITESPACE* value (NEW_LINE | EOI)


"""