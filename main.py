from PyQt6.QtWidgets import *
from dispetcher_logic import *
from graphics import Graphics
from dispetcher import Dispetcher
from journal import Journal
from contex_menu import *
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диспетчер задач")
        self.setFixedSize(800, 600)
        self.tabs()
        
    def tabs(self):
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        dispetcher_widget = Dispetcher()
        graphics_widget = Graphics()
        journal_widget = Journal()
        
        self.tab_widget.addTab(dispetcher_widget, "Процессы")
        self.tab_widget.addTab(graphics_widget, "Производительность")
        self.tab_widget.addTab(journal_widget, "Журнал приложений")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
