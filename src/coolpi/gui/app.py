import os
import sys

import PySide6.QtCore
from PySide6.QtWidgets import QApplication

from coolpi.gui.gui import AppView
from coolpi.gui.model import Model
from coolpi.gui.controller import Controller

class GUI:

    def __init__(self):

        self.app = QApplication()
        self.view = AppView(self.app)
        self.model = Model()
        self.controller = Controller(self.app, self.view, self.model)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

def main():
    
    gui = GUI()
    gui.run()
    
if __name__ == "__main__":
    #print(PySide6.__version__) # Prints PySide6 version
    #print(PySide6.QtCore.__version__) # Prints the Qt version used to compile PySide6
    #os.system('cls' if os.name == 'nt' else 'clear')
    main()