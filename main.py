# Project Structure:
# it_troubleshoot_tool/
# ├── main.py
# ├── requirements.txt
# ├── README.md
# ├── config/
# │   └── settings.py
# ├── core/
# │   ├── __init__.py
# │   ├── base_tab.py
# │   └── logger.py
# ├── network/
# │   ├── __init__.py
# │   ├── network_tab.py
# │   └── network_tools.py
# └── ui/
#     ├── __init__.py
#     └── main_window.py

# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow

class ITTroubleshootApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Sigma's IT Toolkit")
        self.app.setApplicationVersion("1.1.0")
        self.main_window = MainWindow()
        
    def run(self):
        self.main_window.show()
        return self.app.exec_()

if __name__ == "__main__":
    app = ITTroubleshootApp()
    sys.exit(app.run())

# requirements.txt
# PyQt5==5.15.10
# python-nmap==0.7.1
# requests==2.31.0