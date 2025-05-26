# ui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QMenuBar, QAction, QMessageBox,
                            QSplitter, QTextEdit, QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from network.network_tab import NetworkTab
from core.logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "1.0.0"
        self.logger = Logger()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"IT Troubleshoot Tool v{self.version}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for tabs and output
        splitter = QSplitter(Qt.Vertical)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add Network tab
        self.network_tab = NetworkTab(self.logger)
        self.tab_widget.addTab(self.network_tab, "Network Testing")
        
        # Create output section
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        # Output controls
        controls_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Output")
        self.copy_btn = QPushButton("Copy Output")
        self.debug_btn = QPushButton("Toggle Debug")
        self.debug_btn.setCheckable(True)
        
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.copy_btn)
        controls_layout.addWidget(self.debug_btn)
        controls_layout.addStretch()
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555;
            }
        """)
        
        output_layout.addLayout(controls_layout)
        output_layout.addWidget(self.output_text)
        
        # Add to splitter
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(output_widget)
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter)
        
        # Setup connections
        self.setup_connections()
        
        # Setup menu
        self.setup_menu()
        
        # Connect logger to output
        self.logger.message_logged.connect(self.append_output)
        
    def setup_connections(self):
        self.clear_btn.clicked.connect(self.clear_output)
        self.copy_btn.clicked.connect(self.copy_output)
        self.debug_btn.toggled.connect(self.toggle_debug)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def append_output(self, message):
        self.output_text.append(message)
        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.End)
        self.output_text.setTextCursor(cursor)
        
    def clear_output(self):
        self.output_text.clear()
        self.logger.log("Output cleared", "INFO")
        
    def copy_output(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.logger.log("Output copied to clipboard", "INFO")
        
    def toggle_debug(self, enabled):
        self.logger.set_debug_mode(enabled)
        status = "enabled" if enabled else "disabled"
        self.logger.log(f"Debug mode {status}", "INFO")
        
    def show_about(self):
        QMessageBox.about(self, "About IT Troubleshoot Tool", 
                         f"IT Troubleshoot Tool v{self.version}\n\n"
                         "A comprehensive tool for system administrators\n"
                         "to perform network diagnostics and troubleshooting.\n\n"
                         "Features:\n"
                         "• Network Testing (Ping, Traceroute, Port Scan)\n"
                         "• Debug logging\n"
                         "• Easy result copying\n\n"
                         "Created for efficient IT troubleshooting workflows.")

# ui/__init__.py
# Empty file to make it a package