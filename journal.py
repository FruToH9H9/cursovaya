from PyQt6.QtWidgets import *
import pyqtgraph as pg
import sys
import journal_logic

class Journal(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
    
    def UI(self):
        self.layout = QGridLayout()
        win = pg.GraphicsLayoutWidget(title="Real-time Plot")
        plot = win.addPlot(title="CPU Usage (%)")
        curve = plot.plot(pen='y')