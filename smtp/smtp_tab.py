# smtp/smtp_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QGridLayout,
                            QCheckBox, QSpinBox, QComboBox, QTextEdit,
                            QFormLayout, QFrame)
from PyQt5.QtCore import Qt
from core.base_tab import BaseTab
from smtp.smtp_tools import SMTPTools

class SMTPTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.smtp_tools = SMTPTools(logger)
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Server Configuration Section
        server_group = QGroupBox("SMTP Server Configuration")
        server_layout = QGridLayout(server_group)
        
        # Server and port
        server_layout.addWidget(QLabel("Server:"), 0, 0)
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("smtp.gmail.com, mail.company.com, etc.")
        server_layout.addWidget(self.server_edit, 0, 1, 1, 2)
        
        server_layout.addWidget(QLabel("Port:"), 0, 3)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.addItems(["587", "465", "25", "2525"])
        server_layout.addWidget(self.port_combo, 0, 4)
        
        # Encryption options
        server_layout.addWidget(QLabel("Encryption:"), 1, 0)
        self.tls_checkbox = QCheckBox("Use TLS (STARTTLS)")
        self.ssl_checkbox = QCheckBox("Use SSL")
        server_layout.addWidget(self.tls_checkbox, 1, 1)
        server_layout.addWidget(self.ssl_checkbox, 1, 2)
        
        # Timeout
        server_layout.addWidget(QLabel("Timeout:"), 1, 3)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setSuffix(" sec")
        server_layout.addWidget(self.timeout_spin, 1, 4)
        
        layout.addWidget(server_group)
        
        # Authentication Section
        auth_group = QGroupBox("Authentication (Optional)")
        auth_layout = QGridLayout(auth_group)
        
        auth_layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("your.email@domain.com")
        auth_layout.addWidget(self.username_edit, 0, 1)
        
        auth_layout.addWidget(QLabel("Password:"), 0, 2)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        auth_layout.addWidget(self.password_edit, 0, 3)
        
        layout.addWidget(auth_group)
        
        # Email Testing Section
        email_group = QGroupBox("Test Email Configuration")
        email_layout = QGridLayout(email_group)
        
        email_layout.addWidget(QLabel("From:"), 0, 0)
        self.from_edit = QLineEdit()
        self.from_edit.setPlaceholderText("sender@domain.com")
        email_layout.addWidget(self.from_edit, 0, 1)
        
        email_layout.addWidget(QLabel("To:"), 0, 2)
        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("recipient@domain.com")
        email_layout.addWidget(self.to_edit, 0, 3)
        
        email_layout.addWidget(QLabel("Subject:"), 1, 0)
        self.subject_edit = QLineEdit()
        self.subject_edit.setText("SigmaToolkit SMTP Test")
        email_layout.addWidget(self.subject_edit, 1, 1, 1, 3)
        
        layout.addWidget(email_group)
        
        # Testing Actions Section
        actions_group = QGroupBox("SMTP Testing Actions")
        actions_layout = QGridLayout(actions_group)
        
        # Row 1: Basic tests
        self.connect_btn = QPushButton("Test Connection")
        self.auth_btn = QPushButton("Test Auth")
        self.send_btn = QPushButton("Send Test Email")
        self.mx_btn = QPushButton("Check MX Records")
        
        actions_layout.addWidget(self.connect_btn, 0, 0)
        actions_layout.addWidget(self.auth_btn, 0, 1)
        actions_layout.addWidget(self.send_btn, 0, 2)
        actions_layout.addWidget(self.mx_btn, 0, 3)
        
        # Row 2: Advanced tests
        self.ports_btn = QPushButton("Scan SMTP Ports")
        self.comprehensive_btn = QPushButton("Comprehensive Test")
        
        actions_layout.addWidget(self.ports_btn, 1, 0)
        actions_layout.addWidget(self.comprehensive_btn, 1, 1, 1, 2)
        
        layout.addWidget(actions_group)
        
        # Quick Presets Section
        presets_group = QGroupBox("Quick Server Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        self.gmail_btn = QPushButton("Gmail")
        self.outlook_btn = QPushButton("Outlook.com")
        self.office365_btn = QPushButton("Office 365")
        self.yahoo_btn = QPushButton("Yahoo")
        self.custom_btn = QPushButton("Clear All")
        
        presets_layout.addWidget(self.gmail_btn)
        presets_layout.addWidget(self.outlook_btn)
        presets_layout.addWidget(self.office365_btn)
        presets_layout.addWidget(self.yahoo_btn)
        presets_layout.addWidget(self.custom_btn)
        presets_layout.addStretch()
        
        layout.addWidget(presets_group)
        
        # SMTP Information Section
        info_group = QGroupBox("SMTP Testing Guide")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QTextEdit()
        info_text.setMaximumHeight(100)
        info_text.setReadOnly(True)
        info_text.setText(
            "SMTP Testing Tips:\n"
            "• Port 587: Modern SMTP with STARTTLS (recommended)\n"
            "• Port 465: SMTP over SSL (legacy but still used)\n"
            "• Port 25: Plain SMTP (often blocked by ISPs)\n"
            "• Use 'Comprehensive Test' for complete server analysis\n"
            "• Check MX records first to find the mail server for a domain"
        )
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Style the buttons
        self.style_buttons()
        
    def style_buttons(self):
        # Main action buttons
        main_button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        # Test action buttons (different color)
        test_button_style = """
            QPushButton {
                background-color: #d83b01;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #c23101;
            }
            QPushButton:pressed {
                background-color: #a62d01;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        # Preset buttons
        preset_button_style = """
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6b0e;
            }
            QPushButton:pressed {
                background-color: #0c5a0c;
            }
        """
        
        # Apply styles
        for btn in [self.connect_btn, self.auth_btn, self.send_btn, self.mx_btn, 
                   self.ports_btn, self.comprehensive_btn]:
            btn.setStyleSheet(test_button_style)
            
        for btn in [self.gmail_btn, self.outlook_btn, self.office365_btn, 
                   self.yahoo_btn, self.custom_btn]:
            btn.setStyleSheet(preset_button_style)
        
    def setup_connections(self):
        # Test action connections
        self.connect_btn.clicked.connect(self.test_connection)
        self.auth_btn.clicked.connect(self.test_authentication)
        self.send_btn.clicked.connect(self.send_test_email)
        self.mx_btn.clicked.connect(self.check_mx_records)
        self.ports_btn.clicked.connect(self.scan_smtp_ports)
        self.comprehensive_btn.clicked.connect(self.comprehensive_test)
        
        # Preset connections
        self.gmail_btn.clicked.connect(lambda: self.load_preset("gmail"))
        self.outlook_btn.clicked.connect(lambda: self.load_preset("outlook"))
        self.office365_btn.clicked.connect(lambda: self.load_preset("office365"))
        self.yahoo_btn.clicked.connect(lambda: self.load_preset("yahoo"))
        self.custom_btn.clicked.connect(self.clear_all_fields)
        
        # SMTP tools connections
        self.smtp_tools.result_ready.connect(self.handle_result)
        
        # Encryption checkbox logic
        self.tls_checkbox.toggled.connect(self.on_tls_toggled)
        self.ssl_checkbox.toggled.connect(self.on_ssl_toggled)
        
        # Auto-fill from email when username changes
        self.username_edit.textChanged.connect(self.auto_fill_from_email)
        
    def on_tls_toggled(self, checked):
        if checked:
            self.ssl_checkbox.setChecked(False)
            if self.port_combo.currentText() == "465":
                self.port_combo.setCurrentText("587")
                
    def on_ssl_toggled(self, checked):
        if checked:
            self.tls_checkbox.setChecked(False)
            if self.port_combo.currentText() == "587":
                self.port_combo.setCurrentText("465")
                
    def auto_fill_from_email(self, text):
        """Auto-fill 'From' email when username changes"""
        if "@" in text and not self.from_edit.text():
            self.from_edit.setText(text)
        
    def load_preset(self, provider):
        """Load predefined SMTP settings"""
        presets = {
            "gmail": {
                "server": "smtp.gmail.com",
                "port": "587",
                "tls": True,
                "ssl": False
            },
            "outlook": {
                "server": "smtp-mail.outlook.com",
                "port": "587", 
                "tls": True,
                "ssl": False
            },
            "office365": {
                "server": "smtp.office365.com",
                "port": "587",
                "tls": True,
                "ssl": False
            },
            "yahoo": {
                "server": "smtp.mail.yahoo.com",
                "port": "587",
                "tls": True,
                "ssl": False
            }
        }
        
        if provider in presets:
            preset = presets[provider]
            self.server_edit.setText(preset["server"])
            self.port_combo.setCurrentText(preset["port"])
            self.tls_checkbox.setChecked(preset["tls"])
            self.ssl_checkbox.setChecked(preset["ssl"])
            self.info(f"Loaded {provider.title()} SMTP settings")
            
    def clear_all_fields(self):
        """Clear all input fields"""
        self.server_edit.clear()
        self.port_combo.setCurrentText("587")
        self.username_edit.clear()
        self.password_edit.clear()
        self.from_edit.clear()
        self.to_edit.clear()
        self.subject_edit.setText("SigmaToolkit SMTP Test")
        self.tls_checkbox.setChecked(False)
        self.ssl_checkbox.setChecked(False)
        self.info("All fields cleared")
        
    def handle_result(self, message, level):
        if level == "SUCCESS":
            self.success(message)
        elif level == "ERROR":
            self.error(message)
        elif level == "WARNING":
            self.warning(message)
        else:
            self.info(message)
    
    def get_server_config(self):
        """Get current server configuration"""
        return {
            'server': self.server_edit.text().strip(),
            'port': int(self.port_combo.currentText()),
            'use_tls': self.tls_checkbox.isChecked(),
            'use_ssl': self.ssl_checkbox.isChecked(),
            'timeout': self.timeout_spin.value(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'from_email': self.from_edit.text().strip(),
            'to_email': self.to_edit.text().strip(),
            'subject': self.subject_edit.text().strip()
        }
    
    def test_connection(self):
        config = self.get_server_config()
        if not config['server']:
            self.error("Please enter SMTP server address")
            return
            
        self.connect_btn.setEnabled(False)
        self.info(f"Testing connection to {config['server']}:{config['port']}...")
        
        self.smtp_tools.test_connection(
            config['server'], config['port'], 
            config['use_tls'], config['use_ssl'], config['timeout']
        )
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.connect_btn.setEnabled(True))
    
    def test_authentication(self):
        config = self.get_server_config()
        if not config['server']:
            self.error("Please enter SMTP server address")
            return
        if not config['username'] or not config['password']:
            self.error("Please enter username and password")
            return
            
        self.auth_btn.setEnabled(False)
        self.info(f"Testing authentication for {config['username']}...")
        
        self.smtp_tools.test_authentication(
            config['server'], config['port'], config['username'], config['password'],
            config['use_tls'], config['use_ssl'], config['timeout']
        )
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.auth_btn.setEnabled(True))
    
    def send_test_email(self):
        config = self.get_server_config()
        if not config['server']:
            self.error("Please enter SMTP server address")
            return
        if not config['username'] or not config['password']:
            self.error("Please enter username and password")
            return
        if not config['from_email'] or not config['to_email']:
            self.error("Please enter both 'From' and 'To' email addresses")
            return
            
        self.send_btn.setEnabled(False)
        self.info(f"Sending test email from {config['from_email']} to {config['to_email']}...")
        
        self.smtp_tools.send_test_email(
            config['server'], config['port'], config['username'], config['password'],
            config['from_email'], config['to_email'], config['subject'],
            config['use_tls'], config['use_ssl'], config['timeout']
        )
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10000, lambda: self.send_btn.setEnabled(True))
    
    def check_mx_records(self):
        # Extract domain from server or from email
        domain = ""
        if self.from_edit.text() and "@" in self.from_edit.text():
            domain = self.from_edit.text().split("@")[1]
        elif self.to_edit.text() and "@" in self.to_edit.text():
            domain = self.to_edit.text().split("@")[1]
        elif self.server_edit.text():
            # Try to extract domain from server name
            server = self.server_edit.text()
            if server.startswith("smtp."):
                domain = server[5:]  # Remove "smtp." prefix
            elif server.startswith("mail."):
                domain = server[5:]  # Remove "mail." prefix
            else:
                domain = server
        
        if not domain:
            self.error("Please enter an email address or domain to check MX records")
            return
            
        self.mx_btn.setEnabled(False)
        self.info(f"Checking MX records for {domain}...")
        
        self.smtp_tools.check_mx_records(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.mx_btn.setEnabled(True))
    
    def scan_smtp_ports(self):
        config = self.get_server_config()
        if not config['server']:
            self.error("Please enter SMTP server address")
            return
            
        self.ports_btn.setEnabled(False)
        self.info(f"Scanning SMTP ports on {config['server']}...")
        
        self.smtp_tools.test_port_connectivity(config['server'])
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(8000, lambda: self.ports_btn.setEnabled(True))
    
    def comprehensive_test(self):
        config = self.get_server_config()
        if not config['server']:
            self.error("Please enter SMTP server address")
            return
            
        self.comprehensive_btn.setEnabled(False)
        self.info("Starting comprehensive SMTP test...")
        
        self.smtp_tools.comprehensive_smtp_test(
            config['server'], config['port'], config['username'], config['password'],
            config['from_email'], config['to_email'], config['use_tls'], config['use_ssl']
        )
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(15000, lambda: self.comprehensive_btn.setEnabled(True))