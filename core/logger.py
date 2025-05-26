# core/logger.py
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
import threading

class Logger(QObject):
    message_logged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.debug_mode = False
        self.lock = threading.Lock()
        
    def set_debug_mode(self, enabled):
        with self.lock:
            self.debug_mode = enabled
            
    def log(self, message, level="INFO"):
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] [{level}] {message}"
            self.message_logged.emit(formatted_message)
            
    def debug(self, message):
        if self.debug_mode:
            self.log(message, "DEBUG")
            
    def info(self, message):
        self.log(message, "INFO")
        
    def warning(self, message):
        self.log(message, "WARNING")
        
    def error(self, message):
        self.log(message, "ERROR")
        
    def success(self, message):
        self.log(message, "SUCCESS")

# core/base_tab.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject

class BaseTab(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def log(self, message, level="INFO"):
        self.logger.log(message, level)
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def success(self, message):
        self.logger.success(message)

# core/__init__.py
# Empty file to make it a package