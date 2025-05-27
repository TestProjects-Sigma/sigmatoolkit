# ui/main_window.py - COMPLETE FIX TO AVOID IMPORT ERROR
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QMenuBar, QAction, QMessageBox,
                            QSplitter, QTextEdit, QHBoxLayout, QPushButton,
                            QApplication, QLabel, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
from network.network_tab import NetworkTab
from dns.dns_tab import DNSTab
from smtp.smtp_tab import SMTPTab
from speedtest.speedtest_tab import SpeedTestTab

# Try to import the mail tab, but handle gracefully if not available
try:
    from mail.mail_tab import MailTab
    MAIL_TAB_AVAILABLE = True
except ImportError:
    MAIL_TAB_AVAILABLE = False
    print("⚠️ Mail tab not available - run setup script first")

from core.logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "1.4.0" if MAIL_TAB_AVAILABLE else "1.3.0"
        self.logger = Logger()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"SigmaToolkit v{self.version}")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for tabs and output (horizontal split)
        splitter = QSplitter(Qt.Horizontal)
        
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
        
        # Add Mail Header Analysis tab (if available)
        if MAIL_TAB_AVAILABLE:
            self.mail_tab = MailTab(self.logger)
            self.tab_widget.addTab(self.mail_tab, "📨 Mail Analysis")
        
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
        self.output_text.setFont(QFont("Consolas", 11))
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumWidth(500)
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
        
        # Add to splitter
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(output_widget)
        splitter.setSizes([900, 700])
        
        # Make the splitter movable and set minimum sizes
        splitter.setChildrenCollapsible(False)
        self.tab_widget.setMinimumWidth(650)
        output_widget.setMinimumWidth(400)
        
        main_layout.addWidget(splitter)
        
        # Setup connections
        self.setup_connections()
        
        # Setup menu
        self.setup_menu()
        
        # Connect logger to output
        self.logger.message_logged.connect(self.append_output)
        
        # Show welcome message
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """Show welcome message"""
        QTimer.singleShot(1000, self._delayed_welcome)
        
    def _delayed_welcome(self):
        """Delayed welcome message"""
        self.logger.info(f"🎉 Welcome to SigmaToolkit v{self.version}!")
        
        if MAIL_TAB_AVAILABLE:
            self.logger.info("✨ NEW: Mail Header Analysis tab with comprehensive email diagnostics")
            self.logger.info("📨 Analyze email headers, SPF/DKIM/DMARC, delivery paths, and spam indicators")
            self.logger.info("🔍 Complete toolkit: Network → DNS → SMTP → Speed → Mail Analysis")
        else:
            self.logger.warning("📨 Mail Analysis tab not available")
            self.logger.info("💡 To enable: Run the mail module setup script")
            self.logger.info("🔍 Current toolkit: Network → DNS → SMTP → Speed Testing")
            
        self.logger.info("💡 Ready for advanced troubleshooting workflows!")
        
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
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        if MAIL_TAB_AVAILABLE:
            mail_analysis_action = QAction('Mail Header Analysis', self)
            mail_analysis_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
            tools_menu.addAction(mail_analysis_action)
            tools_menu.addSeparator()
        
        export_all_action = QAction('Export All Results', self)
        export_all_action.triggered.connect(self.export_all_results)
        tools_menu.addAction(export_all_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        if MAIL_TAB_AVAILABLE:
            mail_help_action = QAction('Mail Analysis Help', self)
            mail_help_action.triggered.connect(self.show_mail_help)
            help_menu.addAction(mail_help_action)
        
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
        
    def export_all_results(self):
        """Export all results from all tabs"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export All Results", 
                f"sigmatoolkit_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"SigmaToolkit v{self.version} - Complete Results Export\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # Export output log
                    f.write("CONSOLE OUTPUT:\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.output_text.toPlainText())
                    f.write("\n\n")
                    
                self.logger.success(f"All results exported to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
        
    def show_about(self):
        features_text = """• Network Testing (Ping, Traceroute, Port Scan)
• DNS Testing (Forward/Reverse, MX, SPF, TXT, NS, CNAME, AAAA)
• SMTP Testing (Connection, Auth, Email Sending, MX Validation)
• Speed Testing (Internet, LAN, Latency, Real-time Monitoring)"""

        if MAIL_TAB_AVAILABLE:
            features_text += """
• Mail Analysis (Header Analysis, SPF/DKIM/DMARC, Delivery Path, Spam Detection)"""

        features_text += """
• Debug logging and easy result copying"""

        version_history = """v1.3.0 - Added comprehensive speed testing with real-time displays
v1.2.0 - Added SMTP testing capabilities
v1.1.0 - Added DNS testing capabilities
v1.0.0 - Initial release with network tools"""

        if MAIL_TAB_AVAILABLE:
            version_history = f"v1.4.0 - Added comprehensive mail header analysis and email authentication\n{version_history}"

        QMessageBox.about(self, "About SigmaToolkit", 
                         f"SigmaToolkit v{self.version}\n\n"
                         "Sigma's IT Swiss Army Knife\n"
                         "A comprehensive tool for system administrators\n"
                         "to perform network, DNS, email, speed, and mail diagnostics.\n\n"
                         f"Features:\n{features_text}\n\n"
                         f"Version History:\n{version_history}\n\n"
                         "Created for efficient IT troubleshooting workflows.")
    
    def show_mail_help(self):
        """Show help for mail analysis features"""
        if not MAIL_TAB_AVAILABLE:
            QMessageBox.information(self, "Mail Analysis Not Available", 
                                  "The Mail Header Analysis feature is not currently available.\n\n"
                                  "To enable this feature:\n"
                                  "1. Run the mail module setup script\n"
                                  "2. Restart SigmaToolkit\n\n"
                                  "The setup script will create the necessary mail analysis modules.")
            return
            
        help_text = """📨 MAIL HEADER ANALYSIS HELP

The Mail Analysis tab provides comprehensive email diagnostics:

📧 HEADER ANALYSIS:
• Paste email headers from 'View Source' or 'Show Original'
• Analyzes delivery path, authentication, and security
• Identifies potential issues and suspicious patterns

🔐 EMAIL AUTHENTICATION:
• SPF: Validates sending IP against DNS records
• DKIM: Checks cryptographic signatures for integrity
• DMARC: Analyzes domain policies for handling failures

🛤️ DELIVERY PATH:
• Traces email route through servers
• Calculates delivery delays and identifies bottlenecks
• Detects potential mail loops or routing issues

🛡️ SPAM ANALYSIS:
• IP reputation checking
• Content pattern analysis
• Blacklist verification

💡 TIPS:
• Use 'Load Sample' to test with example headers
• Enable all checkboxes for comprehensive analysis
• Export results for documentation and reports
• Combine with SMTP testing for complete email diagnostics"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Mail Analysis Help")
        msg.setText("Mail Header Analysis Help")
        msg.setDetailedText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()