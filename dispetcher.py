import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from dispetcher_logic import *
import sys
import os


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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диспетчер задач")
        self.setFixedSize(800, 600)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(self)
        central_widget.setLayout(self.grid_layout)

        self.table = CustomTableWidget()
        self.table.setColumnCount(7)
        self.table.setSortingEnabled(True)
        self.table.supportedDropActions()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['PID', 'Имя', 'ЦП', 'Память', 'Диск', 'Сеть', 'Энергопотребление'])
        self.table.setColumnHidden(0, True)
        self.grid_layout.addWidget(self.table, 0, 0)

        #Для нужд
        self.selected_name = None
        
        #таймер
        self.timer_clock = 5000
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(self.timer_clock)
        
    def restore_selection(self, name):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1) 
            if item and str(item.text()) == name:
                self.table.selectRow(row)  
                break

    def update_table(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            self.selected_name = str(self.table.item(selected_items[0].row(), 1).text())
        else:
            self.selected_name = None
            
        logic = dispetcher_logic()
        info = logic.info_zadachi()
        self.table.setRowCount(len(info))
        for i, row in enumerate(info):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))  
        
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.set_cell_color(row, col, self.table.item(row, col))
        
        if self.selected_name is not None:
            self.restore_selection(self.selected_name)
                
        self.table.resizeColumnsToContents()
    
    def set_cell_color(self, row, column, item):
        value = item.text()
        list_signs = ['%', ' MB', ' MB/s', ' Mb/s']
        value_list = [5, 100, 1, 0.3] #Колонны: ЦП, Память, Диск, Сеть
        color_logic = dispetcher_logic()
        if 1 < column < 6:
            color_logic.paint(value=value, compare_to=value_list[column-2], item=item, sign=list_signs[column-2])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())