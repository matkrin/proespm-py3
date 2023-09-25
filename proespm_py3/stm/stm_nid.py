from typing import Optional
import numpy as np
import os
import re
from dateutil import parser
from numpy._typing import NDArray
from .stm import StmImage


FLOAT_REGEX = re.compile(r"[+-]?([0-9]*[.])?[0-9]+")
UNITS_REGEX = re.compile(r"[a-zA-Zµ]+")


class NanosurfNid:
    def __init__(self, filepath: str):
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.png_save_dir = os.path.join(self.dirname, "nanonis_nid")

        self.m_id = self.filename
        self.slide_num: Optional[int] = None

        with open(filepath, "rb") as f:
            content = f.read()

        content_list = content.split(b"\r\n\r\n")
        header = get_header(content_list)

        file_meta = get_file_meta(content_list)
        self.op_mode = file_meta["Op. mode"]

        self.xsize = read_float_from_string(file_meta["Image size"])
        xsize_units = read_units_from_string(file_meta["Image size"])
        if xsize_units == "µm":
            self.xsize *= 1000
        self.ysize = self.xsize

        scan_dir_up_down = file_meta["Scan direction"]

        self.xoffset = read_float_from_string(file_meta["X-Pos"])
        xoffset_units = read_units_from_string(file_meta["X-Pos"])
        if xoffset_units == "µm":
            self.xoffset *= 1000

        self.yoffset = read_float_from_string(file_meta["Y-Pos"])
        y_offset_units = read_units_from_string(file_meta["Y-Pos"])
        if y_offset_units == "µm":
            self.yoffset *= 1000

        self.tilt = read_float_from_string(file_meta["Rotation"])
        self.line_time = read_float_from_string(file_meta["Time/Line"])
        self.speed = (
            self.line_time * read_float_from_string(file_meta["Lines"]) / 1000
        )

        self.datetime = parser.parse(
            file_meta["Date"] + " " + file_meta["Time"]
        )
        self.bias = read_float_from_string(file_meta["Tip voltage"])
        # current; or setpoint AFM in %
        self.current = read_float_from_string(file_meta["Setpoint"])
        self.p_gain = read_float_from_string(file_meta["P-Gain"])
        self.i_gain = read_float_from_string(file_meta["I-Gain"])

        channels = get_channels(header)
        channel_meta_list = get_channels_meta(content_list, channels)
        self.xres = int(channel_meta_list[0]["Points"])
        self.yres = int(channel_meta_list[0]["Lines"])

        # `Z-Axis` for topo AFM/STM, `Tip Current` for current STM, `Amplitude` for AFM
        scantype = channel_meta_list[0]["Dim2Name"]
        datatype = (
            np.int16 if channel_meta_list[0]["SaveBits"] == "16" else np.int32
        )

        for channel in channel_meta_list:
            assert self.xres == int(channel["Points"])
            assert self.yres == int(channel["Lines"])

        img_data_block = get_img_data_block(content_list)
        img_data_list = read_img_data(img_data_block, datatype, 4)

        fw_idx = None
        bw_idx = None
        for i, ch in enumerate(channel_meta_list):
            if ch["Dim2Name"] == "Z-Axis":
                if ch["Frame"] == "Scan forward":
                    fw_idx = i
                elif ch["Frame"] == "Scan backward":
                    bw_idx = i

        assert fw_idx is not None
        assert bw_idx is not None
        img_data_fw = (
            img_data_list[fw_idx]
            .reshape(self.yres, self.xres)
            .astype(np.float64)
        )
        img_data_bw = (
            img_data_list[bw_idx]
            .reshape(self.yres, self.xres)
            .astype(np.float64)
        )

        # Plotting is from bottom left corner
        if file_meta["Scan direction"] == "Down":
            img_data_fw = np.flip(img_data_fw, axis=0)
            img_data_bw = np.flip(img_data_bw, axis=0)

        self.img_data_fw = StmImage(img_data_fw, self.xsize)
        self.img_data_bw = StmImage(img_data_bw, self.xsize)


def get_header(content_list: list[bytes]) -> list[bytes]:
    return content_list[0].split(b"\r\n")


def get_channels(header: list[bytes]) -> list[bytes]:
    channels: list[bytes] = []
    for i in header:
        if b"Ch" in i:
            channels.append(i.split(b"=")[1])

    return channels


def get_file_meta(content_list: list[bytes]) -> dict[str, str]:
    file_meta: dict[str, str] = {}
    for block in content_list:
        if block.startswith(b"[DataSet-Info"):
            split = block.split(b"\r\n")
            for line in split[1:]:
                if not line.startswith(b"-"):
                    key, val = line.decode().split("=")
                    file_meta[key] = val
            break
    return file_meta


def get_channels_meta(content_list: list[bytes], channels: list[bytes]) -> list[dict[str, str]]:
    channels_meta_list: list[dict[str, str]] = []
    k = 0
    for block in content_list:
        if k == len(channels):
            break
        channel = b"[" + channels[k] + b"]"
        if block.startswith(channel):
            split = block.split(b"\r\n")
            channels_meta: dict[str, str] = {}
            for s in split[1:]:
                ident, val = s.decode().split("=")
                channels_meta[ident] = val

            channels_meta_list.append(channels_meta)
            k += 1
    return channels_meta_list


def get_img_data_block(content_list: list[bytes]) -> bytes:
    data_block = content_list[-1]
    # first 4 bytes are some identifier
    assert data_block[:4] == b"\r\n#!"
    return data_block[4:]


def read_img_data(img_data_block, dtype, num_channels) -> list[NDArray]:
    img_data = np.frombuffer(img_data_block, dtype=dtype)
    return np.array_split(img_data, num_channels)


def read_float_from_string(text: str) -> float:
    return float(FLOAT_REGEX.match(text).group(0))  # type: ignore


def read_units_from_string(text: str) -> str:
    return UNITS_REGEX.findall(text)[0]  # type: ignore
