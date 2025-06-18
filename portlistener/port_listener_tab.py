# portlistener/port_listener_tab.py
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QTextEdit, QGroupBox, QFrame,
                            QMessageBox, QCheckBox, QSpinBox, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from core.base_tab import BaseTab
from .port_listener_tools import PortListenerTools
import ctypes

class PortListenerTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.port_tools = PortListenerTools(logger)
        self.is_listening = False
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the Port Listener user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🔌 Port Listener Tool")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #0078d4; padding: 10px;")
        layout.addWidget(title_label)
        
        # Firewall Warning Panel
        self.create_warning_panel(layout)
        
        # Configuration Panel
        self.create_config_panel(layout)
        
        # Control Panel
        self.create_control_panel(layout)
        
        # Status Panel
        self.create_status_panel(layout)
        
        # Connection Log Panel
        self.create_log_panel(layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def create_warning_panel(self, layout):
        """Create firewall warning panel"""
        warning_group = QGroupBox("⚠️ Important Information")
        warning_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ffc107;
                border-radius: 5px;
                margin: 5px 0px;
                background-color: #fff3cd;
                color: #856404;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        warning_layout = QVBoxLayout()
        
        warning_text = QLabel(
            "• Ensure Windows Firewall allows inbound connections on the specified port\n"
            "• Ports below 1024 require Administrator privileges\n" 
            "• You may need to create a firewall rule or run as administrator\n"
            "• Test with: telnet your-server-ip port-number"
        )
        warning_text.setStyleSheet("color: #856404; font-weight: normal; padding: 5px;")
        warning_text.setWordWrap(True)
        
        warning_layout.addWidget(warning_text)
        warning_group.setLayout(warning_layout)
        layout.addWidget(warning_group)
        
    def create_config_panel(self, layout):
        """Create configuration panel"""
        config_group = QGroupBox("🔧 Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #007bff;
                border-radius: 5px;
                margin: 5px 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        config_layout = QVBoxLayout()
        
        # IP Address Configuration
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setToolTip("Use 0.0.0.0 to listen on all interfaces, or specify a specific IP")
        self.ip_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        ip_layout.addWidget(self.ip_input)
        config_layout.addLayout(ip_layout)
        
        # Port Configuration
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("443")
        self.port_input.setToolTip("Port to listen on (1-65535). Ports below 1024 require admin privileges")
        self.port_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        config_layout.addLayout(port_layout)
        
        # Response Type
        response_layout = QHBoxLayout()
        response_layout.addWidget(QLabel("Response Type:"))
        self.response_combo = QComboBox()
        self.response_combo.addItems(["HTTP OK", "Echo", "Silent"])
        self.response_combo.setToolTip("Type of response to send to connecting clients")
        self.response_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        response_layout.addWidget(self.response_combo)
        response_layout.addStretch()
        config_layout.addLayout(response_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
    def create_control_panel(self, layout):
        """Create control panel"""
        control_group = QGroupBox("🎮 Controls")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 5px;
                margin: 5px 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        control_layout = QVBoxLayout()
        
        # Button and status layout
        button_layout = QHBoxLayout()
        
        # Start/Stop button
        self.start_stop_btn = QPushButton("🚀 Start Listening")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        # Test button
        self.test_btn = QPushButton("🧪 Test Connection")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        
        button_layout.addWidget(self.start_stop_btn)
        button_layout.addWidget(self.test_btn)
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        
        # Status display
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready to start")
        self.status_label.setStyleSheet("color: #007bff; font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        control_layout.addLayout(status_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
    def create_status_panel(self, layout):
        """Create status information panel"""
        status_group = QGroupBox("📊 Connection Statistics")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #6f42c1;
                border-radius: 5px;
                margin: 5px 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        stats_layout = QHBoxLayout()
        
        # Connection count
        self.connection_count_label = QLabel("Connections: 0")
        self.connection_count_label.setStyleSheet("font-weight: bold; color: #6f42c1;")
        
        # Last connection
        self.last_connection_label = QLabel("Last: None")
        self.last_connection_label.setStyleSheet("font-weight: bold; color: #6f42c1;")
        
        # Uptime
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("font-weight: bold; color: #6f42c1;")
        
        stats_layout.addWidget(self.connection_count_label)
        stats_layout.addWidget(self.last_connection_label)
        stats_layout.addWidget(self.uptime_label)
        stats_layout.addStretch()
        
        status_group.setLayout(stats_layout)
        layout.addWidget(status_group)
        
    def create_log_panel(self, layout):
        """Create connection log panel"""
        log_group = QGroupBox("📝 Connection Log")
        log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #fd7e14;
                border-radius: 5px;
                margin: 5px 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        log_layout = QVBoxLayout()
        
        # Log controls
        log_controls_layout = QHBoxLayout()
        
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.setToolTip("Automatically scroll to newest entries")
        
        self.show_timestamps_cb = QCheckBox("Show timestamps")
        self.show_timestamps_cb.setChecked(True)
        self.show_timestamps_cb.setToolTip("Include timestamps in log entries")
        
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        log_controls_layout.addWidget(self.auto_scroll_cb)
        log_controls_layout.addWidget(self.show_timestamps_cb)
        log_controls_layout.addStretch()
        log_controls_layout.addWidget(self.clear_log_btn)
        
        # Connection log text area
        self.connection_log = QTextEdit()
        self.connection_log.setMaximumHeight(150)
        self.connection_log.setReadOnly(True)
        self.connection_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #555;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                padding: 5px;
            }
        """)
        
        log_layout.addLayout(log_controls_layout)
        log_layout.addWidget(self.connection_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.start_stop_btn.clicked.connect(self.toggle_listening)
        self.test_btn.clicked.connect(self.test_connection)
        self.clear_log_btn.clicked.connect(self.clear_connection_log)
        
        # Connect port tools signals
        self.port_tools.connection_received.connect(self.on_connection_received)
        self.port_tools.error_occurred.connect(self.on_error_occurred)
        self.port_tools.status_changed.connect(self.on_status_changed)
        
    def check_admin_privileges(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def validate_inputs(self):
        """Validate IP and port inputs"""
        ip = self.ip_input.text().strip()
        port_text = self.port_input.text().strip()
        
        # Validate IP
        if ip and ip != "0.0.0.0":
            import socket
            try:
                socket.inet_aton(ip)
            except socket.error:
                raise ValueError("Invalid IP address format")
                
        # Validate port
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Port must be a number")
            raise
            
        # Check for privileged ports
        if port < 1024 and not self.check_admin_privileges():
            raise ValueError(f"Port {port} requires administrator privileges")
            
        return ip, port
        
    def toggle_listening(self):
        """Toggle listening state"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
            
    def start_listening(self):
        """Start the port listener"""
        try:
            ip, port = self.validate_inputs()
            response_type = self.response_combo.currentText()
            
            success = self.port_tools.start_listening(ip, port, response_type)
            
            if success:
                self.is_listening = True
                self.start_stop_btn.setText("🛑 Stop Listening")
                self.start_stop_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #bd2130;
                    }
                """)
                
                self.status_label.setText(f"🟢 Listening on {ip}:{port}")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 12px;")
                
                # Disable inputs
                self.ip_input.setEnabled(False)
                self.port_input.setEnabled(False)
                self.response_combo.setEnabled(False)
                
                self.info(f"Started port listener on {ip}:{port} with {response_type} response")
                self.add_connection_log(f"Started listening on {ip}:{port}")
                
            else:
                self.error("Failed to start port listener")
                
        except ValueError as e:
            self.error(f"Configuration error: {str(e)}")
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            self.error(f"Failed to start listener: {str(e)}")
            
    def stop_listening(self):
        """Stop the port listener"""
        try:
            self.port_tools.stop_listening()
            
            self.is_listening = False
            self.start_stop_btn.setText("🚀 Start Listening")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            
            self.status_label.setText("🔴 Stopped")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 12px;")
            
            # Re-enable inputs
            self.ip_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.response_combo.setEnabled(True)
            
            self.info("Port listener stopped")
            self.add_connection_log("Stopped listening")
            
        except Exception as e:
            self.error(f"Error stopping listener: {str(e)}")
            
    def test_connection(self):
        """Test connection to the listening port"""
        if not self.is_listening:
            QMessageBox.warning(self, "Not Listening", "Port listener is not currently running.")
            return
            
        try:
            ip = self.ip_input.text().strip()
            port = int(self.port_input.text().strip())
            
            # Use localhost if listening on all interfaces
            test_ip = "127.0.0.1" if ip == "0.0.0.0" else ip
            
            success = self.port_tools.test_connection(test_ip, port)
            
            if success:
                self.success(f"Test connection to {test_ip}:{port} successful")
            else:
                self.warning(f"Test connection to {test_ip}:{port} failed")
                
        except Exception as e:
            self.error(f"Test connection failed: {str(e)}")
            
    def clear_connection_log(self):
        """Clear the connection log"""
        self.connection_log.clear()
        self.info("Connection log cleared")
        
    def add_connection_log(self, message):
        """Add entry to connection log"""
        if self.show_timestamps_cb.isChecked():
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
        else:
            log_entry = message
            
        self.connection_log.append(log_entry)
        
        # Auto-scroll if enabled
        if self.auto_scroll_cb.isChecked():
            scrollbar = self.connection_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def on_connection_received(self, client_ip, timestamp):
        """Handle incoming connection"""
        self.add_connection_log(f"Connection from: {client_ip}")
        
        # Update statistics
        stats = self.port_tools.get_statistics()
        self.connection_count_label.setText(f"Connections: {stats['connections']}")
        self.last_connection_label.setText(f"Last: {client_ip}")
        
    def on_error_occurred(self, error_msg):
        """Handle errors from port tools"""
        self.error(f"Port listener error: {error_msg}")
        self.add_connection_log(f"ERROR: {error_msg}")
        
    def on_status_changed(self, uptime):
        """Handle status updates"""
        self.uptime_label.setText(f"Uptime: {uptime}")