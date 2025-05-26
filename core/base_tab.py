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