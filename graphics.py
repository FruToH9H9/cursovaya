from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
import subprocess
import pyqtgraph as pg
import psutil
import GPUtil

class Graphics(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
        self.cpu_data = []
        self.gpu_data = []

        
    def UI(self):
        self.layout = QGridLayout()
        self.cpu_name = self.get_cpu_name()
        self.gpu_names = self.get_gpu_names()
        # CPU
        win_cpu = pg.GraphicsLayoutWidget(title="Real-time CPU Usage Plot")
        plot_cpu = win_cpu.addPlot()
        plot_cpu.setYRange(0, 100)
        plot_cpu.setXRange(0, 20)
        win_cpu.setBackground('lightgray')
        self.curve_cpu = plot_cpu.plot(pen='b')
        self.label_cpu_name = QLabel(f'{self.cpu_name}')
        self.layout.addWidget(self.label_cpu_name, 0, 0)
        self.layout.addWidget(win_cpu, 1, 0)

        # GPU
        win_gpu = pg.GraphicsLayoutWidget(title="Real-time GPU Usage Plot")
        plot_gpu = win_gpu.addPlot()
        plot_gpu.setYRange(0, 100)
        plot_gpu.setXRange(0, 20)
        win_gpu.setBackground('lightgray')
        self.curve_gpu = plot_gpu.plot(pen='b')
        self.label_gpu_name = QLabel(f'{self.gpu_names[0]}')
        self.layout.addWidget(self.label_gpu_name, 2, 0)
        self.layout.addWidget(win_gpu, 3, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.setLayout(self.layout)
        
    def update(self):
        if len(self.cpu_data) == 21:
            self.cpu_data.pop(0)
        self.cpu_data.append(psutil.cpu_percent(interval=0.5))
        self.curve_cpu.setData(self.cpu_data)

        if len(self.gpu_data) == 21:
            self.gpu_data.pop(0)
        gpu_util = self.get_gpu_usage()
        self.gpu_data.append(gpu_util)
        self.curve_gpu.setData(self.gpu_data)

    def get_cpu_name(self):
        cpu_name = subprocess.check_output("wmic cpu get caption", shell=True).decode().strip().split("\n")[1]
        return cpu_name
    
    def get_gpu_names(self):
        gpus = GPUtil.getGPUs()
        gpu_info = []
        for gpu in gpus:
            gpu_info.append(gpu.name)
        return gpu_info

    def get_gpu_usage(self):
        gpus = GPUtil.getGPUs()
        gpu_util = [gpu.memoryUtil * 100 for gpu in gpus]
        return gpu_util[0] if gpu_util else 0

