import numpy as np
import os
import pathlib
import re

FLOAT_REGEX = re.compile(r"[+-]?([0-9]*[.])?[0-9]+")


class NanosurfNid:
    def __init__(self, filepath):
        self.basename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.filename, self.fileext = os.path.splitext(self.basename)
        self.png_save_dir = os.path.join(self.dirname, "nanonis_nid")

        self.m_id = self.filename

        with open(filepath, "rb") as f:
            content = f.read()

        content_list = content.split(b"\r\n\r\n")
        header = get_header(content_list)

        file_meta = get_file_meta(content_list)
        self.mode = file_meta["Op. mode"]
        self.xsize = read_float_from_string(file_meta["Image size"])
        self.ysize = self.xsize
        scan_dir_up_down = file_meta["Scan direction"]
        self.xoffset = read_float_from_string(file_meta["X-Pos"])
        self.yoffset = read_float_from_string(file_meta["Y-Pos"])
        self.tilt = read_float_from_string(file_meta["Rotation"])
        self.line_time = read_float_from_string(file_meta["Time/Line"])
        self.speed = self.line_time * read_float_from_string(
            file_meta["Lines"]
        )

        # TODO make datetime out of it
        self.datetime = file_meta["Date"] + " " + file_meta["Time"]
        # STM and AFM
        self.bias = read_float_from_string(file_meta["Tip voltage"])
        # current; or setpoint AFM in %
        self.current = read_float_from_string(file_meta["Setpoint"])

        channels = get_channels(header)
        channel_meta_list = get_channels_meta(content_list, channels)
        # print(channel_meta_list)
        self.xres = int(channel_meta_list[0]["Points"])
        self.yres = int(channel_meta_list[0]["Lines"])

        # `Z-Axis` for topo AFM/STM, `Tip Current` for current STM, `Amplitude` for AFM
        scantype = channel_meta_list[0]["Dim2Name"]
        print(scantype)
        datatype = (
            np.int16 if channel_meta_list[0]["SaveBits"] == "16" else np.int32
        )

        for channel in channel_meta_list:
            assert self.xres == int(channel["Points"])
            assert self.yres == int(channel["Lines"])
            # channel["Frame"] give fw / bw

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
        self.img_data_fw = img_data_list[fw_idx].reshape(self.yres, self.xres)
        self.img_data_bw = img_data_list[bw_idx].reshape(self.yres, self.xres)

        if file_meta["Scan direction"] == "Up":
            self.img_data_fw = np.flip(self.img_data_fw, axis=0)
            self.img_data_bw = np.flip(self.img_data_bw, axis=0)


def get_header(content_list):
    return content_list[0].split(b"\r\n")


def get_channels(header):
    channels = []
    for i in header:
        if b"Ch" in i:
            channels.append(i.split(b"=")[1])

    return channels


def get_file_meta(content_list):
    file_meta = {}
    for block in content_list:
        if block.startswith(b"[DataSet-Info"):
            split = block.split(b"\r\n")
            for line in split[1:]:
                if not line.startswith(b"-"):
                    key, val = line.decode().split("=")
                    file_meta[key] = val
            break
    return file_meta


def get_channels_meta(content_list, channels):
    channels_meta_list = []
    k = 0
    for block in content_list:
        if k == len(channels):
            break
        channel = b"[" + channels[k] + b"]"
        if block.startswith(channel):
            split = block.split(b"\r\n")
            channels_meta = {}
            for s in split[1:]:
                # print(s.decode().split("="))
                ident, val = s.decode().split("=")
                # print(ident)
                channels_meta[ident] = val

            channels_meta_list.append(channels_meta)
            k += 1
    return channels_meta_list


def get_img_data_block(content_list):
    data_block = content_list[-1]
    # first 4 bytes are some identifier
    assert data_block[:4] == b"\r\n#!"
    return data_block[4:]


def read_img_data(img_data_block, dtype, num_channels) -> list[np.array]:
    img_data = np.frombuffer(img_data_block, dtype=dtype)
    return np.array_split(img_data, num_channels)


def read_float_from_string(text):
    return float(FLOAT_REGEX.match(text).group(0))
