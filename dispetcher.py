import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QBrush, QDesktopServices
import sys
import os
import keyboard


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
        if selected_row >= 0:
            pid = int(self.item(selected_row, 0).text())
            try:
                proc = psutil.Process(pid)
                proc.terminate()  
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                QMessageBox.critical(self, "Ошибка", "Не удалось завершить процесс")
    
    def open_dict(self):
        selected_row = self.currentRow()
        if selected_row >= 0:
            pid = int(self.item(selected_row, 0).text()) 
            try:
                proc = psutil.Process(pid)
                path = proc.exe() 
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))  
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

        self.processes = {}
        self.prev_cpu = {}  
        self.prev_io = {} 
        self.prev_net = {}
        
        self.timer_clock = 3000
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(self.timer_clock)

        self.update_process_list()
        
    def update_process_list(self):
        self.processes = {}
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == "System Idle Process":
                    continue
                proc.cpu_percent(interval=0.0)  
                self.processes[proc.pid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def update_table(self):
        info = self.info_zadachi()
        self.table.setRowCount(len(info))
        for i, row in enumerate(info):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))  
        
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.set_cell_color(row, col, self.table.item(row, col))
                
        self.table.resizeColumnsToContents()
        

    def info_zadachi(self):
        process_dict = {}  # Словарь для группировки процессов по именам

        for pid, proc in list(self.processes.items()):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                memory_info = proc.memory_info().rss / 1024**2 
                cpu_percent = proc.cpu_percent(interval=0.0)  
                cpu_percent = cpu_percent / psutil.cpu_count(logical=True) 

                io_counters = proc.io_counters()
                prev_read, prev_write = self.prev_io.get(pid, (io_counters.read_bytes, io_counters.write_bytes))
                disk_usage = ((io_counters.read_bytes - prev_read) + (io_counters.write_bytes - prev_write)) / 1024**2  # МБ/с
                self.prev_io[pid] = (io_counters.read_bytes, io_counters.write_bytes)
                
                net_counters = proc.io_counters()
                prev_sent, prev_recv = self.prev_net.get(pid, (net_counters.other_bytes, net_counters.read_bytes))
                net_speed = ((net_counters.other_bytes - prev_sent) + (net_counters.read_bytes - prev_recv)) * 8 / 10**6  # Мбит/с
                self.prev_net[pid] = (net_counters.other_bytes, net_counters.read_bytes)
                
                power_usage = self.estimate_power_usage(cpu_percent, net_speed, memory_info)

                if name in process_dict:
                    process_dict[name]['cpu_percent'] += cpu_percent
                    process_dict[name]['memory_info'] += memory_info
                    process_dict[name]['disk_usage'] += disk_usage
                    process_dict[name]['net_speed'] += net_speed
                    process_dict[name]['power_usage'] = self.estimate_power_usage(
                        process_dict[name]['cpu_percent'],
                        process_dict[name]['net_speed'],
                        process_dict[name]['memory_info']
                    )
                else:
                    # Иначе добавляем новый процесс в словарь
                    process_dict[name] = {
                        'cpu_percent': cpu_percent,
                        'memory_info': memory_info,
                        'disk_usage': disk_usage,
                        'net_speed': net_speed,
                        'power_usage': power_usage
                    }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Преобразуем словарь обратно в список для отображения в таблице
        result = []
        for name, values in process_dict.items():
            row = [
                pid,
                name,  # Имя процесса   
                f"{values['cpu_percent']:.2f}%",  # Использование CPU в %
                f"{values['memory_info']:.2f} MB",  # Использование памяти в МБ
                f"{values['disk_usage']:.2f} MB/s",  # Скорость диска в МБ/с
                f"{values['net_speed']:.2f} Mb/s",  # Скорость сети в Мбит/c
                values['power_usage']  # Использование аккумулятора в статусе
            ]
            result.append(row)

        return result

    def estimate_power_usage(self, cpu, network, memory):
        power_score = (cpu * 0.7) + (network * 0.1) + (memory * 0.1)
        if power_score < 10:
            return "Очень низкое"
        elif power_score < 30:
            return "Низкое"
        elif power_score < 60:
            return "Среднее"
        elif power_score < 90:
            return "Высокое"
        else:
            return "Очень высокое"

    def set_cell_color(self, row, column, item):
        value = item.text()
        if column == 2:  # ЦП
            value = float(value.replace('%', ''))
            if value > 50.0:
                item.setBackground(QBrush(QColor(255, 0, 0)))  # Красный
            elif value > 20.0:
                item.setBackground(QBrush(QColor(255, 255, 0)))  # Желтый
            elif value > 5.0:
                item.setBackground(QBrush(QColor(0, 255, 0)))  # Зеленый
                
        elif column == 3:  # Память
            value = float(value.replace(' MB', ''))
            if value > 2000:
                item.setBackground(QBrush(QColor(255, 0, 0)))  
            elif value > 500:
                item.setBackground(QBrush(QColor(255, 255, 0)))  
            elif value > 100:
                item.setBackground(QBrush(QColor(0, 255, 0)))  
                  
        elif column == 4:  # Диск (МБ/с)
            value = float(value.replace(' MB/s', ''))
            if value > 50:
                item.setBackground(QBrush(QColor(255, 0, 0)))  
            elif value > 10:
                item.setBackground(QBrush(QColor(255, 255, 0)))  
            elif value > 1:
                item.setBackground(QBrush(QColor(0, 255, 0)))  
                  
        elif column == 5:  # Сеть (Мбит/с)
            value = float(value.replace(' Mb/s', ''))
            if value > 10:
                item.setBackground(QBrush(QColor(255, 0, 0)))  
            elif value > 1:
                item.setBackground(QBrush(QColor(255, 255, 0)))  
            elif value > 0.3:
                item.setBackground(QBrush(QColor(0, 255, 0)))  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())