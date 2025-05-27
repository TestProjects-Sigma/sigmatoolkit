# ui/main_window.py - UPDATED FOR v1.3.0
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QMenuBar, QAction, QMessageBox,
                            QSplitter, QTextEdit, QHBoxLayout, QPushButton,
                            QApplication, QLabel)  # Added QLabel here
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from network.network_tab import NetworkTab
from dns.dns_tab import DNSTab
from smtp.smtp_tab import SMTPTab
from speedtest.speedtest_tab import SpeedTestTab  # Import the new Speedtest tab
from core.logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "1.3.0"  # Updated version for Speedtest features
        self.logger = Logger()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"SigmaToolkit v{self.version}")
        self.setGeometry(100, 100, 1500, 1000)  # Larger window for better layout
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for tabs and output (horizontal split)
        splitter = QSplitter(Qt.Horizontal)  # Changed to horizontal
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add Network tab
        self.network_tab = NetworkTab(self.logger)
        self.tab_widget.addTab(self.network_tab, "🌐 Network Testing")
        
        # Add DNS tab
        self.dns_tab = DNSTab(self.logger)
        self.tab_widget.addTab(self.dns_tab, "🔍 DNS Testing")
        
        # Add SMTP tab
        self.smtp_tab = SMTPTab(self.logger)
        self.tab_widget.addTab(self.smtp_tab, "📧 SMTP Testing")
        
        # Add Speedtest tab
        self.speedtest_tab = SpeedTestTab(self.logger)
        self.tab_widget.addTab(self.speedtest_tab, "⚡ Speed Testing")
        
        # Create output section with larger, better layout
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        # Output header
        output_header = QLabel("📊 Real-time Results & Logs")
        output_header.setFont(QFont("Arial", 12, QFont.Bold))
        output_header.setStyleSheet("color: #0078d4; padding: 5px;")
        output_layout.addWidget(output_header)
        
        # Output controls
        controls_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Output")
        self.copy_btn = QPushButton("Copy Output")
        self.debug_btn = QPushButton("Toggle Debug")
        self.debug_btn.setCheckable(True)
        
        # Style the control buttons
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
            }
        """
        
        self.clear_btn.setStyleSheet(button_style)
        self.copy_btn.setStyleSheet(button_style)
        self.debug_btn.setStyleSheet(button_style)
        
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.copy_btn)
        controls_layout.addWidget(self.debug_btn)
        controls_layout.addStretch()
        
        # Output text area - much larger and better styled
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 11))  # Slightly larger font
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumWidth(500)  # Minimum width
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #0078d4;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)
        
        output_layout.addLayout(controls_layout)
        output_layout.addWidget(self.output_text)
        
        # Add to splitter with much larger output area
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(output_widget)
        splitter.setSizes([800, 700])  # 53% tabs, 47% output - Much larger output!
        
        # Make the splitter movable and set minimum sizes
        splitter.setChildrenCollapsible(False)  # Prevent collapsing
        self.tab_widget.setMinimumWidth(600)     # Minimum tab area
        output_widget.setMinimumWidth(400)       # Minimum output area
        
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
        QMessageBox.about(self, "About SigmaToolkit", 
                         f"SigmaToolkit v{self.version}\\n\\n"
                         "Sigma's IT Swiss Army Knife\\n"
                         "A comprehensive tool for system administrators\\n"
                         "to perform network, DNS, email, and speed diagnostics.\\n\\n"
                         "Features:\\n"
                         "• Network Testing (Ping, Traceroute, Port Scan)\\n"
                         "• DNS Testing (Forward/Reverse, MX, SPF, TXT, NS, CNAME, AAAA)\\n"
                         "• SMTP Testing (Connection, Auth, Email Sending, MX Validation)\\n"
                         "• Speed Testing (Internet, LAN, Latency, Real-time Monitoring)\\n"
                         "• Debug logging and easy result copying\\n\\n"
                         "Version History:\\n"
                         "v1.3.0 - Added comprehensive speed testing with real-time displays\\n"
                         "v1.2.0 - Added SMTP testing capabilities\\n"
                         "v1.1.0 - Added DNS testing capabilities\\n"
                         "v1.0.0 - Initial release with network tools\\n\\n"
                         "Created for efficient IT troubleshooting workflows.")