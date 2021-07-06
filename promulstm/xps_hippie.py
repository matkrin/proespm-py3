import os
import numpy as np


class XpsHippie:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.splitext(self.filepath)[0]
        self.data = None
        self.read_xps_hippie(filepath)

    
    def read_xps_hippie(self, filepath):
        """
        """
        with open(filepath) as f:
            f.readline()
            num_regions = int(f.readline().split('=')[1])
            f.readline()

            self.data = []
            for i in range(num_regions):
                scan_dict = dict(xps='maxlab_hippie')

                f.readline()
                scan_dict['region'] = f.readline().rstrip().strip('[]').split(' ')[1]
                scan_dict['region_name'] = f.readline().split('=')[1].rstrip()
                scan_dict['dim_name'] = f.readline().split('=')[1].rstrip()
                scan_dict['dim_size'] = int(f.readline().split('=')[1])
                scan_dict['dim_scale'] = [float(x) for x in
                                          (f.readline().split('=')[1].split(' '))]
                f.readline()
                f.readline()
                scan_dict['region_name_alt'] = f.readline().split('=')[1].rstrip()
                scan_dict['lens_mode'] = f.readline().split('=')[1].rstrip()
                scan_dict['e_pass'] = int(f.readline().split('=')[1])
                scan_dict['sweeps'] = int(f.readline().split('=')[1])
                scan_dict['excitation_energy'] = float(f.readline().split('=')[1])
                scan_dict['energy_scale'] = f.readline().split('=')[1].rstrip()
                scan_dict['aquisition_mode'] = f.readline().split('=')[1].rstrip()
                scan_dict['energy_unit'] = f.readline().split('=')[1].rstrip()
                scan_dict['center_energy'] = float(f.readline().split('=')[1])
                scan_dict['low_energy'] = float(f.readline().split('=')[1])
                scan_dict['high_energy'] = float(f.readline().split('=')[1])
                scan_dict['step'] = float(f.readline().split('=')[1])
                scan_dict['step_time'] = float(f.readline().split('=')[1])    # dwell?
                scan_dict['detect_first_x_ch'] = int(f.readline().split('=')[1])
                scan_dict['detect_last_x_ch'] = int(f.readline().split('=')[1])
                scan_dict['detect_first_y_ch'] = int(f.readline().split('=')[1])
                scan_dict['detect_last_y_ch'] = int(f.readline().split('=')[1])
                scan_dict['num_slices'] = int(f.readline().split('=')[1])
                scan_dict['save_path'] = f.readline().split('=')[1].rstrip()
                scan_dict['sequence'] = f.readline().split('=')[1].rstrip()
                scan_dict['spec_name'] = f.readline().split('=')[1].rstrip()
                scan_dict['instrument'] = f.readline().split('=')[1].rstrip()
                scan_dict['location'] = f.readline().split('=')[1].rstrip()
                scan_dict['user'] = f.readline().split('=')[1].rstrip()
                scan_dict['sample'] = f.readline().split('=')[1].rstrip()
                scan_dict['comments'] = f.readline().split('=')[1].rstrip()
                scan_dict['date'] = f.readline().split('=')[1].rstrip()
                scan_dict['time'] = f.readline().split('=')[1].rstrip()
                scan_dict['time_per_spec_ch'] = float(f.readline().split('=')[1])
                scan_dict['detec_mode'] = f.readline().split('=')[1].rstrip()
                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                scan_dict['xps_data'] = np.array([float(x) for x in
                                                  f.readline().strip().split('  ')])
                for _ in range(scan_dict['dim_size']-1):
                    line = [float(x) for x in f.readline().strip().split('  ')]
                    arr_line = np.array(line)
                    scan_dict['xps_data'] = np.vstack((scan_dict['xps_data'], arr_line))

                self.data.append(scan_dict)
