from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
from graphics_logic import *
import pyqtgraph as pg
import psutil
import subprocess
from pyqtgraph.Qt import QtWidgets


class Graphics(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
        self.data=[]
        
    def UI(self):
        self.layout = QGridLayout()
        win = pg.GraphicsLayoutWidget(title="Real-time Plot")
        plot = win.addPlot()
        plot.setYRange(0, 100)
        plot.setXRange(0, 20)
        win.setBackground('lightgray')
        self.curve = plot.plot(pen='b')
        self.layout.addWidget(win)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.setLayout(self.layout)
        
    def update(self):
        if len(self.data) == 21:
            self.data.pop(0)
        self.data.append(psutil.cpu_percent(interval=0.5))
        self.curve.setData(self.data)
        