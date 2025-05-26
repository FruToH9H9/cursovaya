from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
import subprocess
import pyqtgraph as pg
import psutil
import GPUtil

class Graphics(QWidget):
    def __init__(self):
        super().__init__()
        self.CPU_x = 20
        self.GPU_x = 20
        self.UI()
        self.cpu_data = []
        self.gpu_data = []

        
    def UI(self):
        self.layout = QGridLayout()
        self.cpu_name = self.get_cpu_name()
        self.gpu_names = self.get_gpu_names()
        # CPU
        radioButton_cpu = QSpinBox()
        radioButton_cpu.setValue(self.CPU_x)
        radioButton_cpu.valueChanged.connect(self.CPU_x_changed)
        radioButton_cpu.setMaximum(100)
        win_cpu = pg.GraphicsLayoutWidget(title="Real-time CPU Usage Plot")
        self.plot_cpu = win_cpu.addPlot()
        self.plot_cpu.setYRange(0, 100)
        self.plot_cpu.setXRange(0, self.CPU_x)
        win_cpu.setBackground('lightgray')
        self.curve_cpu = self.plot_cpu.plot(pen='b')
        self.label_cpu_name = QLabel(f'{self.cpu_name}')
        self.layout.addWidget(self.label_cpu_name, 0, 0)
        self.layout.addWidget(radioButton_cpu, 1, 0)
        self.layout.addWidget(win_cpu, 2, 0)

        # GPU
        radioButton_gpu = QSpinBox()
        radioButton_gpu.setValue(self.GPU_x)
        radioButton_gpu.valueChanged.connect(self.GPU_x_changed)
        radioButton_gpu.setMaximum(100)
        win_gpu = pg.GraphicsLayoutWidget(title="Real-time GPU Usage Plot")
        self.plot_gpu = win_gpu.addPlot()
        self.plot_gpu.setYRange(0, 100)
        self.plot_gpu.setXRange(0, self.GPU_x)
        win_gpu.setBackground('lightgray')
        self.curve_gpu = self.plot_gpu.plot(pen='b')
        self.label_gpu_name = QLabel(f'{self.gpu_names[0]}')
        self.layout.addWidget(self.label_gpu_name, 3, 0)
        self.layout.addWidget(radioButton_gpu, 4, 0)
        self.layout.addWidget(win_gpu, 5, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.setLayout(self.layout)
        
    def GPU_x_changed(self, value):
        self.GPU_x = value
        self.plot_gpu.setXRange(0, self.GPU_x)
        
    def CPU_x_changed(self, value):
        self.CPU_x = value
        self.plot_cpu.setXRange(0, self.CPU_x)
        
    def update(self):
        if len(self.cpu_data) == self.CPU_x+1:
            self.cpu_data.pop(0)
        self.cpu_data.append(psutil.cpu_percent(interval=0.5))
        self.curve_cpu.setData(self.cpu_data)

        if len(self.gpu_data) == self.GPU_x+1:
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

