import numpy as np
import os
import datetime
from bokeh.plotting import figure
from bokeh.embed import components


class XpsVtStm:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.splitext(self.filepath)[0]
        self.data = None
        self.read_xps_vtstm(filepath)

    
    def read_xps_vtstm(self, filepath):
        """
        """
        with open(filepath) as f:
            scan_num = f.read().count('Region')
            f.seek(0) 

            self.data = []
            for i in range(scan_num):
                scan_dict = dict(xps='vtstm')
                line1 = f.readline().split('\t')
                line1 = [x.rstrip('\n') for x in line1]
                line2 = f.readline().split('\t')
                line2 = [x.rstrip('\n') for x in line2]

                scan_dict.update(dict(zip(line1, line2)))

                line3 = f.readline().split('\t')
                line3 = [x.rstrip('\n') for x in line3]
                line4 = f.readline().split('\t')
                line4 = [x.rstrip('\n') for x in line4]

                scan_dict.update(dict(zip(line3, line4)))

                data_header = f.readline().split('\t')
                data_header = [x.rstrip('\n') for x in data_header]

                start = float(scan_dict['Start'])
                end = float(scan_dict['End'])
                step = float(scan_dict['Step'])

                num_lines = int(abs(start - end) / step)

                xps_data = np.array([float(x) for x in f.readline().split('\t')])
                for _ in range(num_lines):
                    line = [float(x) for x in f.readline().split('\t')]
                    arr_line = np.array(line)
                    xps_data = np.vstack((xps_data, arr_line))

                scan_dict.update(dict(xps_data=xps_data))

                self.data.append(scan_dict)


class XpsScan:
    def __init__(self, data, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.datetime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')

        for key, value in data.items():
            setattr(self, key.lower(), value)

        self.m_id = f'{os.path.splitext(self.filename)[0]}_{self.region}'

        if self.xps == 'vtstm':
            self.e_pass = data['CAE/CRR']

        if self.xps == 'maxlab_hippie':
            self.datetime = f'{self.date} {self.time}'

        self.plot()


    def plot(self):
        """
        """
        x = self.xps_data[:,0]
        y = self.xps_data[:,1]

        if self.xps == 'vtstm':
            x_range = (x[-1], x[0])
        elif self.xps == 'maxlab_hippie':
            x_range = (x[0], x[-1])
            
        plot = figure(
            plot_width = 1000,
            plot_height = 540,
            x_axis_label = 'E_b / eV',
            y_axis_label = 'Intensity / arb. units',
            x_range = x_range,
            sizing_mode = 'scale_width',
            tools = 'pan, wheel_zoom, box_zoom, crosshair, save, reset, hover'
        )
        plot.toolbar.active_drag = "auto"
        plot.toolbar.active_scroll = "auto"
        plot.toolbar.active_inspect = None
        plot.toolbar.logo = None
        plot.background_fill_alpha = 0
        #plot.circle(x, y, size=2)
        plot.line(x, y)
        plot.toolbar.active_scroll = "auto"
        self.script, self.div = components(plot, wrap_script=True)


    def save_plain_data(self, directory):
        plain_data_dir = os.path.join(
            directory,
            self.filename.split('.')[0] + "_plain_data"
        )
        if not os.path.exists(plain_data_dir):
            os.makedirs(plain_data_dir)
        np.savetxt(
            os.path.join(plain_data_dir, self.m_id + ".txt"),
            self.xps_data
        )
