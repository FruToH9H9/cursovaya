from PyQt6.QtWidgets import QGridLayout, QTableWidget, QWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer
from journal_logic import journal_logic
class Journal(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
    
    def UI(self):
        self.layout = QGridLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Имя", "Время жизни"])
        self.layout.addWidget(self.table, 0, 0)
        
        timer_interval = 2000
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(timer_interval)
    
    def update_table(self):
        logic = journal_logic()
        info = logic.update_list()
        self.table.setRowCount(len(info))
        for row, (name, data) in enumerate(info.items()):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{data['time']:.2f} sec"))