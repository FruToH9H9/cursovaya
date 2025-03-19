import psutil
import os
from PyQt6.QtWidgets import QMenu, QTableWidget, QMessageBox

class CustomTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        action1 = context_menu.addAction("Завершить процесс")
        action2 = context_menu.addAction("Открыть расположение файла")
        
        action1.triggered.connect(self.kill_proccess)
        action2.triggered.connect(self.open_dict)
        
        context_menu.exec(event.globalPos())
        
    def kill_proccess(self):
        selected_row = self.currentRow()
        pid = int(self.item(selected_row, 0).text())
        try:
            proc = psutil.Process(pid)
            proc.terminate()  
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            QMessageBox.critical(self, "Ошибка", "Не удалось завершить процесс")
    
    def open_dict(self):
        selected_row = self.currentRow()
        pid = int(self.item(selected_row, 0).text()) 
        try:
            proc = psutil.Process(pid)
            path = proc.exe() 
            os.startfile(os.path.dirname(path))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть расположение файла")
