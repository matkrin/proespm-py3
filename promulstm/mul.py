import struct
import os
from datetime import datetime
import numpy as np


class Mul:

    def __init__(self, file):
        self.file = file
        self.img_lst = self.read_mul(file)
        self.datetime = datetime.utcfromtimestamp(
            os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')

    def read_mul(self, file):
        filesize = os.path.getsize(file)
        mul_block = 128

        with open(file, 'rb') as f:
            nr = struct.unpack('h', f.read(2))[0]
            adr = struct.unpack('i', f.read(4))[0]

        with open(file, 'rb') as f:
            block_counter = 0
            img_lst = []

            if adr == 3:
                f.read(mul_block * adr)
                block_counter += adr

            while block_counter*mul_block < filesize:
                img_num = struct.unpack('h', f.read(2))[0]
                size = struct.unpack('h', f.read(2))[0]		#in mul_blocks
                xres = struct.unpack('h', f.read(2))[0]		#in pixels
                yres = struct.unpack('h', f.read(2))[0]		#in pixels
                zres = struct.unpack('h', f.read(2))[0]

                y = struct.unpack('h', f.read(2))[0]
                m = struct.unpack('h', f.read(2))[0]
                d = struct.unpack('h', f.read(2))[0]
                hh = struct.unpack('h', f.read(2))[0]
                mm = struct.unpack('h', f.read(2))[0]
                ss = struct.unpack('h', f.read(2))[0]

                xsize = struct.unpack('h', f.read(2))[0]	#in Angstrom
                ysize  = struct.unpack('h', f.read(2))[0]	#in Angstrom
                xoffset = struct.unpack('h', f.read(2))[0]
                yoffset = struct.unpack('h', f.read(2))[0]
                zscale = struct.unpack('h', f.read(2))[0]	#in V
                tilt = struct.unpack('h', f.read(2))[0]		#in deg

                speed = struct.unpack('h', f.read(2))[0]
                bias = struct.unpack('h', f.read(2))[0]
                current = struct.unpack('h', f.read(2))[0]

                sample_string = ''.join([chr(i) for i in f.read(21)])
                title_string = ''.join([chr(i) for i in f.read(21)])

                postpr = struct.unpack('h', f.read(2))[0]
                postd1 = struct.unpack('h', f.read(2))[0]
                mode = struct.unpack('h', f.read(2))[0]
                currfac = struct.unpack('h', f.read(2))[0]
                num_pointscans = struct.unpack('h', f.read(2))[0]
                unitnr = struct.unpack('h', f.read(2))[0]
                version = struct.unpack('h', f.read(2))[0]

                spare_48 = struct.unpack('h', f.read(2))[0]	#useful in point scans?
                spare_49 = struct.unpack('h', f.read(2))[0]
                spare_50 = struct.unpack('h', f.read(2))[0]
                spare_51 = struct.unpack('h', f.read(2))[0]
                spare_52 = struct.unpack('h', f.read(2))[0]
                spare_53 = struct.unpack('h', f.read(2))[0]
                spare_54 = struct.unpack('h', f.read(2))[0]
                spare_55 = struct.unpack('h', f.read(2))[0]
                spare_56 = struct.unpack('h', f.read(2))[0]
                spare_57 = struct.unpack('h', f.read(2))[0]
                spare_58 = struct.unpack('h', f.read(2))[0]
                spare_59 = struct.unpack('h', f.read(2))[0]
                gain = struct.unpack('h', f.read(2))[0]
                spare_61 = struct.unpack('h', f.read(2))[0]
                spare_62 = struct.unpack('h', f.read(2))[0]
                spare_63 = struct.unpack('h', f.read(2))[0]

                speed *= 0.01					#in seconds
                line_time = speed / yres			#in seconds
                bias = -bias / 3.2768				#in mV
                current *= currfac * 0.01			#in nA

                img_data = np.frombuffer(f.read(xres*2), dtype=np.int16)
                for i in range(0, yres - 1):
                    line = np.frombuffer(f.read(xres*2), dtype=np.int16)
                    img_data = np.vstack([img_data, line])

                img_data = img_data.astype('float64')
                img_data *= -0.1/1.36 * zscale/200  	#in Angstrom

                if num_pointscans > 0:
                    for i in range(0, num_pointscans):
                        ps_size = struct.unpack('h', f.read(2))[0]
                        ps_type = struct.unpack('h', f.read(2))[0]
                        ps_time4scan = struct.unpack('h', f.read(2))[0]

                        ps_minv = struct.unpack('h', f.read(2))[0]
                        ps_maxv = struct.unpack('h', f.read(2))[0]

                        ps_xpos = struct.unpack('h', f.read(2))[0]
                        ps_ypos = struct.unpack('h', f.read(2))[0]

                        ps_dz = struct.unpack('h', f.read(2))[0]
                        ps_delay = struct.unpack('h', f.read(2))[0]
                        ps_version = struct.unpack('h', f.read(2))[0]
                        ps_indendelay = struct.unpack('h', f.read(2))[0]
                        ps_xposend = struct.unpack('h', f.read(2))[0]
                        ps_yposend = struct.unpack('h', f.read(2))[0]

                        ps_vt_fw = struct.unpack('h', f.read(2))[0]
                        ps_it_fw = struct.unpack('h', f.read(2))[0]
                        ps_vt_bw = struct.unpack('h', f.read(2))[0]
                        ps_it_bw = struct.unpack('h', f.read(2))[0]
                        ps_lscan = struct.unpack('h', f.read(2))[0]

                        f.read(mul_block - 18*2)	#spare
                        ps_data = np.frombuffer(f.read(ps_size*2), dtype=np.int16)

                block_counter += size

                img_lst.append({
                                "filename": file,
                                "basename": os.path.basename(file),
                                "img_id": os.path.basename(file)[:-4] + "_" + str(img_num),
                                "img_num": img_num,
                                "size": size,
                                "xres": xres,
                                "yres": yres,
                                "zres": zres,
                                "datetime": datetime(y, m, d, hh, mm, ss),
                                "xsize": xsize,
                                "ysize": ysize,
                                "yoffset": yoffset,
                                "xoffset": xoffset,
                                "zscale": zscale,
                                "tilt": tilt,
                                "speed": speed,
                                "line_time": line_time,
                                "bias": bias,
                                "current": current,
                                "sample_string": sample_string,
                                "title_string": title_string,
                                "postpr": postpr,
                                "postd1": postd1,
                                "mode": mode,
                                "currfac": currfac,
                                "num_pointscans": num_pointscans,
                                "unitnr": unitnr,
                                "version": version,
                                "gain": gain,
                                "img_data": img_data
                                })
        return img_lst
