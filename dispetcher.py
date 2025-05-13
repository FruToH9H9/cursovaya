from PyQt6.QtWidgets import QWidget, QGridLayout, QTableWidgetItem
from PyQt6.QtCore import QTimer
from dispetcher_logic import *
from contex_menu import *
import sys


class Dispetcher(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
    
    def UI(self):
        self.grid_layout = QGridLayout(self)
        
        self.table = CustomTableWidget()
        self.table.setColumnCount(7)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['PID', 'Имя', 'ЦП', 'Память', 'Диск', 'Сеть', 'Энергопотребление'])
        self.table.setColumnHidden(0, True)
        self.grid_layout.addWidget(self.table, 0, 0)

        #Для нужд
        self.selected_name = None
        
        self.update_table()
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
                item = self.table.item(row, col)
                if item is not None:
                    self.set_cell_color(col, item)
        
        if self.selected_name is not None:
            self.restore_selection(self.selected_name)
                
        self.table.resizeColumnsToContents()
        
    def set_cell_color(self, column: int, item):
        value = item.text()
        list_signs = ['%', ' MB', ' MB/s', ' Mb/s']
        value_list = [5.0, 100.0, 1.0, 0.3] #Колонны: ЦП, Память, Диск, Сеть
        color_logic = dispetcher_logic()
        
        if 1 < column < 6:
            data = {
            'value': value,
            'compare_to':value_list[column-2],
            'item': item,
            'sign':list_signs[column-2]
            }
            color_logic.paint(data)