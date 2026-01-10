import re
from typing import Any, Hashable, Self, final

import numpy as np
from dateutil import parser

from proespm.config import Config
from proespm.fileinfo import Fileinfo
from proespm.spm.spm import SpmImage


FLOAT_REGEX = re.compile(r"[+-]?([0-9]*[.])?[0-9]+")
UNITS_REGEX = re.compile(r"[a-zA-Zµ°]+")


@final
class SpmNid:
    def __init__(self, filepath: str):
        self.ident = "NID"
        self.fileinfo = Fileinfo(filepath)

        self.m_id = self.fileinfo.filename
        self.slide_num: int | None = None

        with open(filepath, "rb") as f:
            content = f.read()

        content_list = content.split(b"\r\n\r\n")
        header = _get_header(content_list)

        file_meta = _get_file_meta(content_list)
        self.op_mode = file_meta["Op. mode"]

        if self.op_mode == "Dynamic Force":
            self.cantilever = file_meta["Cantilever type"]
            self.amp_ctrl_mode = file_meta["Ampl. Ctrl. mode"]
            self.excitation_amp = _read_float_from_string(
                file_meta["Excitation ampl."]
            )
        elif self.op_mode == "Static Force":
            self.cantilever = file_meta["Cantilever type"]
            self.amp_ctrl_mode = file_meta["Ampl. Ctrl. mode"]

        self.xsize = _read_float_from_string(file_meta["Image size"])
        xsize_units = _read_units_from_string(file_meta["Image size"])
        if xsize_units == "µm":
            self.xsize *= 1000
        self.ysize = self.xsize

        self.scan_dir_up_down = file_meta["Scan direction"]

        self.xoffset = _read_float_from_string(file_meta["X-Pos"])
        xoffset_units = _read_units_from_string(file_meta["X-Pos"])
        if xoffset_units == "µm":
            self.xoffset *= 1000

        self.yoffset = _read_float_from_string(file_meta["Y-Pos"])
        y_offset_units = _read_units_from_string(file_meta["Y-Pos"])
        if y_offset_units == "µm":
            self.yoffset *= 1000

        self.rotation = _read_float_from_string(file_meta["Rotation"])
        self.line_time = _read_float_from_string(file_meta["Time/Line"])
        self.scan_duration = (
            self.line_time
            * 2
            * _read_float_from_string(file_meta["Lines"])
            / 1000
        )

        self.datetime = parser.parse(
            file_meta["Date"] + " " + file_meta["Time"]
        )
        self.bias = _read_float_from_string(file_meta["Tip voltage"])
        # current; or setpoint AFM in %
        self.current = _read_float_from_string(file_meta["Setpoint"])
        self.p_gain = _read_float_from_string(file_meta["P-Gain"])
        self.i_gain = _read_float_from_string(file_meta["I-Gain"])

        channels = get_channels(header)
        channel_meta_list = _get_channels_meta(content_list, channels)
        self.xres = int(channel_meta_list[0]["Points"])
        self.yres = int(channel_meta_list[0]["Lines"])

        # `Z-Axis` for topo AFM/STM, `Tip Current` for current STM, `Amplitude` for AFM
        # scantype = channel_meta_list[0]["Dim2Name"]
        save_bits = int(channel_meta_list[0]["SaveBits"])
        datatype = np.int16 if save_bits == 16 else np.int32

        for channel in channel_meta_list:
            assert self.xres == int(channel["Points"])
            assert self.yres == int(channel["Lines"])

        num_channels = len(channel_meta_list)
        bytes_to_read = (
            int(self.xres * self.yres * save_bits / 8) * num_channels
        )
        img_data_start = len(content) - bytes_to_read
        img_data = np.frombuffer(content[img_data_start:], dtype=datatype)
        img_data_list = np.array_split(img_data, num_channels)

        fw_idx = None
        bw_idx = None
        for i, ch in enumerate(channel_meta_list):
            if ch["Dim2Name"] in ["Z-Axis", "Topography"]:
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

        self.img_data_fw = SpmImage(np.flip(img_data_fw, axis=0), self.xsize)
        self.img_data_bw = SpmImage(np.flip(img_data_bw, axis=0), self.xsize)

    def process(self, config: Config) -> Self:
        _ = (
            self.img_data_fw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )
        _ = (
            self.img_data_bw.corr_plane()
            .corr_lines_median()
            .corr_plane()
            .corr_lines_median()
            .plot(config.colormap, config.colorrange)
        )

        return self

    def template_name(self) -> str:
        return "nid.j2"


def _get_header(content_list: list[bytes]) -> list[bytes]:
    return content_list[0].split(b"\r\n")


def get_channels(header: list[bytes]) -> list[bytes]:
    channels: list[bytes] = []
    for i in header:
        if b"Ch" in i:
            channels.append(i.split(b"=")[1])

    return channels


def _get_file_meta(content_list: list[bytes]) -> dict[str, str]:
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


def _get_channels_meta(
    content_list: list[bytes], channels: list[bytes]
) -> list[dict[str, str]]:
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


def _read_float_from_string(text: str) -> float:
    return float(FLOAT_REGEX.match(text).group(0))  # pyright: ignore[reportOptionalMemberAccess]


def _read_units_from_string(text: str) -> str:
    return UNITS_REGEX.findall(text)[0]  # pyright: ignore[reportAny]
