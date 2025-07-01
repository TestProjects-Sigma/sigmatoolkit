# ad/ad_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QSpinBox, QLabel, QProgressBar, QMessageBox,
    QSplitter, QHeaderView, QTextEdit, QFrame, QTabWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont
from core.base_tab import BaseTab
from .ad_tools import ADPasswordTools
import json
from datetime import datetime
from pathlib import Path

class NumericTableWidgetItem(QTableWidgetItem):
    """Custom table widget item for proper numerical sorting."""
    
    def __init__(self, text, numeric_value):
        super().__init__(text)
        self.numeric_value = numeric_value
    
    def __lt__(self, other):
        """Custom comparison for sorting."""
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        return super().__lt__(other)

class ADPasswordTab(BaseTab):
    """Active Directory Password Expiry Checker Tab"""
    
    def __init__(self, logger):
        super().__init__(logger)
        self.ad_tools = ADPasswordTools(logger)
        self.worker = None
        self.refresh_timer = QTimer()
        self.users_data = []
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the UI layout"""
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Reduce spacing between elements
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # More compact header or remove it entirely
        # header = QLabel("🔐 AD Password Checker")
        # header.setFont(QFont("Arial", 10, QFont.Bold))
        # header.setStyleSheet("color: #0078d4; padding: 2px; margin: 0px;")
        # layout.addWidget(header)
        
        # Create main splitter without header
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Configuration
        config_widget = self.create_config_panel()
        splitter.addWidget(config_widget)
        
        # Right panel - Results with tabs
        results_widget = self.create_results_panel()
        splitter.addWidget(results_widget)
        
        splitter.setSizes([400, 800])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def create_config_panel(self):
        """Create the configuration panel"""
        config_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Reduce spacing between groups
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Connection Settings Group - more compact
        conn_group = QGroupBox("🌐 Connection Settings")
        conn_group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        conn_layout = QFormLayout()
        conn_layout.setVerticalSpacing(6)  # Reduce spacing between form rows
        
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("dc01.company.com")
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(636)
        
        self.use_ssl_check = QCheckBox("Use SSL/TLS (Recommended)")
        self.use_ssl_check.setChecked(True)
        
        self.domain_edit = QLineEdit()
        self.domain_edit.setPlaceholderText("COMPANY")
        
        self.base_dn_edit = QLineEdit()
        self.base_dn_edit.setPlaceholderText("DC=company,DC=com")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("serviceaccount")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        
        conn_layout.addRow("Server:", self.server_edit)
        conn_layout.addRow("Port:", self.port_spin)
        conn_layout.addRow("", self.use_ssl_check)
        conn_layout.addRow("Domain:", self.domain_edit)
        conn_layout.addRow("Base DN:", self.base_dn_edit)
        conn_layout.addRow("Username:", self.username_edit)
        conn_layout.addRow("Password:", self.password_edit)
        
        conn_group.setLayout(conn_layout)
        
        # Application Settings Group - more compact
        app_group = QGroupBox("⚙️ Application Settings")
        app_group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        app_layout = QFormLayout()
        app_layout.setVerticalSpacing(6)  # Reduce spacing between form rows
        
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(30, 3600)
        self.refresh_interval_spin.setValue(300)  # 5 minutes default
        self.refresh_interval_spin.setSuffix(" seconds")
        
        self.warning_days_spin = QSpinBox()
        self.warning_days_spin.setRange(1, 365)
        self.warning_days_spin.setValue(14)
        self.warning_days_spin.setSuffix(" days")
        
        app_layout.addRow("", self.auto_refresh_check)
        app_layout.addRow("Refresh Interval:", self.refresh_interval_spin)
        app_layout.addRow("Warning Days:", self.warning_days_spin)
        
        app_group.setLayout(app_layout)
        
        # Control Buttons - more compact
        button_layout = QVBoxLayout()
        button_layout.setSpacing(4)  # Reduce spacing between buttons
        
        self.test_btn = QPushButton("🔍 Test Connection")
        self.save_config_btn = QPushButton("💾 Save Configuration")
        self.load_config_btn = QPushButton("📂 Load Configuration")
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.export_btn = QPushButton("📤 Export Data")
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
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
        
        for btn in [self.test_btn, self.save_config_btn, self.load_config_btn, 
                   self.refresh_btn, self.export_btn]:
            btn.setStyleSheet(button_style)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        # Status display
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; padding: 5px; font-style: italic;")
        button_layout.addWidget(self.status_label)
        
        # Assemble layout
        layout.addWidget(conn_group)
        layout.addWidget(app_group)
        layout.addLayout(button_layout)
        
        config_widget.setLayout(layout)
        return config_widget
        
    def create_results_panel(self):
        """Create the results panel with tabs"""
        results_widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary statistics
        self.summary_label = QLabel("📊 No data loaded")
        self.summary_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.summary_label.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.summary_label)
        
        # Create tab widget for different views
        self.results_tabs = QTabWidget()
        
        # Users table tab
        self.users_table = self.create_users_table()
        self.results_tabs.addTab(self.users_table, "👥 User List")
        
        # Summary report tab
        self.summary_report = self.create_summary_report()
        self.results_tabs.addTab(self.summary_report, "📋 Summary Report")
        
        # Configuration info tab
        self.config_info = self.create_config_info()
        self.results_tabs.addTab(self.config_info, "⚙️ Configuration")
        
        layout.addWidget(self.results_tabs)
        results_widget.setLayout(layout)
        return results_widget
        
    def create_users_table(self):
        """Create the users data table"""
        table_widget = QWidget()
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        headers = [
            "Username", "Display Name", "Email", "Days Until Expiry",
            "Password Last Set", "Password Expires", "Status"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Username
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Display Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Email
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Days
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Last Set
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Expires
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status
        
        layout.addWidget(self.table)
        table_widget.setLayout(layout)
        return table_widget
        
    def create_summary_report(self):
        """Create summary report text area"""
        summary_widget = QWidget()
        layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Consolas", 10))
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.summary_text)
        summary_widget.setLayout(layout)
        return summary_widget
        
    def create_config_info(self):
        """Create configuration information display"""
        config_widget = QWidget()
        layout = QVBoxLayout()
        
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setFont(QFont("Consolas", 10))
        self.config_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Add refresh config button
        refresh_config_btn = QPushButton("🔄 Refresh Configuration Info")
        refresh_config_btn.clicked.connect(self.update_config_info)
        
        layout.addWidget(refresh_config_btn)
        layout.addWidget(self.config_text)
        config_widget.setLayout(layout)
        return config_widget
        
    def setup_connections(self):
        """Setup signal connections"""
        self.test_btn.clicked.connect(self.test_connection)
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.load_config_btn.clicked.connect(self.load_configuration)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.export_btn.clicked.connect(self.export_data)
        self.auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        self.refresh_timer.timeout.connect(self.refresh_data)
        
    def get_connection_params(self):
        """Get current connection parameters"""
        return {
            "server": self.server_edit.text().strip(),
            "port": self.port_spin.value(),
            "use_ssl": self.use_ssl_check.isChecked(),
            "domain": self.domain_edit.text().strip(),
            "username": self.username_edit.text().strip(),
            "password": self.password_edit.text(),
            "base_dn": self.base_dn_edit.text().strip()
        }
        
    def test_connection(self):
        """Test AD connection"""
        if self.worker and self.worker.isRunning():
            self.info("Connection test already in progress")
            return
            
        params = self.get_connection_params()
        
        # Validate required fields
        required_fields = ["server", "domain", "username", "password", "base_dn"]
        for field in required_fields:
            if not params.get(field):
                self.error(f"Please fill in the {field.replace('_', ' ').title()} field")
                QMessageBox.warning(self, "Configuration Error", 
                                  f"Please fill in the {field.replace('_', ' ').title()} field.")
                return
        
        self.info("🔍 Testing AD connection...")
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.status_label.setText("Testing connection...")
        
        # Start test in worker thread
        self.worker = self.ad_tools.test_connection_async(
            params, self.on_test_success, self.on_test_error
        )
        
    def on_test_success(self, message):
        """Handle successful connection test"""
        self.success(f"✅ Connection test successful: {message}")
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔍 Test Connection")
        self.status_label.setText("Connection test successful")
        QMessageBox.information(self, "Connection Test", f"Success!\n{message}")
        
    def on_test_error(self, error_message):
        """Handle connection test error"""
        self.error(f"❌ Connection test failed: {error_message}")
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔍 Test Connection")
        self.status_label.setText("Connection test failed")
        QMessageBox.critical(self, "Connection Test Failed", error_message)
        
    def refresh_data(self):
        """Refresh AD password data"""
        if self.worker and self.worker.isRunning():
            self.info("Data refresh already in progress")
            return
            
        params = self.get_connection_params()
        
        # Validate required fields
        required_fields = ["server", "domain", "username", "password", "base_dn"]
        for field in required_fields:
            if not params.get(field):
                self.error(f"Please configure the {field.replace('_', ' ').title()} field")
                QMessageBox.warning(self, "Configuration Error", 
                                  f"Please configure the {field.replace('_', ' ').title()} field.")
                return
        
        self.info("🔄 Refreshing password expiry data...")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Refreshing...")
        self.progress_bar.setVisible(True)
        self.status_label.setText("Loading user data...")
        
        # Start data refresh in worker thread
        self.worker = self.ad_tools.get_password_data_async(
            params, self.on_data_received, self.on_data_error, self.on_progress
        )
        
    def on_data_received(self, users_data):
        """Handle received user data"""
        self.users_data = users_data
        self.populate_table(users_data)
        self.update_summary(users_data)
        self.update_summary_report(users_data)
        
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh Data")
        self.status_label.setText(f"Data loaded: {len(users_data)} users")
        
        self.success(f"✅ Password data refreshed - {len(users_data)} users loaded")
        
    def on_data_error(self, error_message):
        """Handle data refresh error"""
        self.error(f"❌ Data refresh failed: {error_message}")
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh Data")
        self.status_label.setText("Data refresh failed")
        QMessageBox.critical(self, "Data Refresh Error", error_message)
        
    def on_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def populate_table(self, users_data):
        """Populate the users table with data"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(users_data))
        
        for row, user in enumerate(users_data):
            # Username
            self.table.setItem(row, 0, QTableWidgetItem(user.get('username', '')))
            
            # Display Name
            self.table.setItem(row, 1, QTableWidgetItem(user.get('display_name', '')))
            
            # Email
            self.table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
            
            # Days until expiry - use custom numeric item for proper sorting
            days = user.get('days_until_expiry', 0)
            if user.get('password_never_expires', False):
                days_item = NumericTableWidgetItem("Never", 999999)
            else:
                days_item = NumericTableWidgetItem(str(days), days)
                
                # Color coding
                if days < 0:
                    days_item.setBackground(Qt.red)
                elif days <= 7:
                    days_item.setBackground(Qt.yellow)
                    
            self.table.setItem(row, 3, days_item)
            
            # Password last set
            last_set = user.get('password_last_set', '')
            if isinstance(last_set, datetime):
                last_set = last_set.strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 4, QTableWidgetItem(str(last_set)))
            
            # Password expires
            expires = user.get('password_expires', '')
            if user.get('password_never_expires', False):
                expires_str = "Never"
            elif isinstance(expires, datetime):
                expires_str = expires.strftime("%Y-%m-%d %H:%M")
            else:
                expires_str = str(expires)
            self.table.setItem(row, 5, QTableWidgetItem(expires_str))
            
            # Status
            if user.get('account_disabled', False):
                status = "Disabled"
            elif user.get('password_never_expires', False):
                status = "Never Expires"
            elif days < 0:
                status = "Expired"
            elif days <= 7:
                status = "Expiring Soon"
            else:
                status = "Active"
            self.table.setItem(row, 6, QTableWidgetItem(status))
        
        self.table.setSortingEnabled(True)
        
        # Force proper sorting for the Days Until Expiry column (column 3)
        # Sort by the most critical first (expired passwords)
        self.table.sortItems(3, Qt.AscendingOrder)
        
    def update_summary(self, users_data):
        """Update summary statistics"""
        total_users = len(users_data)
        expired_count = len([u for u in users_data if u.get('days_until_expiry', 0) < 0])
        expiring_soon = len([u for u in users_data if 0 <= u.get('days_until_expiry', 0) <= 7])
        never_expires = len([u for u in users_data if u.get('password_never_expires', False)])
        disabled = len([u for u in users_data if u.get('account_disabled', False)])
        
        summary_text = (
            f"📊 Total Users: {total_users} | "
            f"🔴 Expired: {expired_count} | "
            f"🟡 Expiring Soon (≤7 days): {expiring_soon} | "
            f"♾️ Never Expires: {never_expires} | "
            f"❌ Disabled: {disabled}"
        )
        self.summary_label.setText(summary_text)
        
    def update_summary_report(self, users_data):
        """Update summary report text"""
        total_users = len(users_data)
        expired_users = [u for u in users_data if u.get('days_until_expiry', 0) < 0]
        expiring_soon = [u for u in users_data if 0 <= u.get('days_until_expiry', 0) <= 7]
        
        report = f"""📋 PASSWORD EXPIRY SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 50}

OVERVIEW:
• Total Users: {total_users}
• Expired Passwords: {len(expired_users)}
• Expiring Soon (≤7 days): {len(expiring_soon)}
• Never Expires: {len([u for u in users_data if u.get('password_never_expires', False)])}
• Disabled Accounts: {len([u for u in users_data if u.get('account_disabled', False)])}

"""
        
        if expired_users:
            report += "🔴 EXPIRED PASSWORDS:\n"
            report += "-" * 25 + "\n"
            for user in expired_users[:10]:  # Show first 10
                days = user.get('days_until_expiry', 0)
                report += f"• {user.get('username', '')} ({user.get('display_name', '')}) - {abs(days)} days ago\n"
            if len(expired_users) > 10:
                report += f"... and {len(expired_users) - 10} more\n"
            report += "\n"
            
        if expiring_soon:
            report += "🟡 EXPIRING SOON:\n"
            report += "-" * 17 + "\n"
            for user in expiring_soon[:10]:  # Show first 10
                days = user.get('days_until_expiry', 0)
                report += f"• {user.get('username', '')} ({user.get('display_name', '')}) - {days} days\n"
            if len(expiring_soon) > 10:
                report += f"... and {len(expiring_soon) - 10} more\n"
            report += "\n"
            
        report += """📋 RECOMMENDATIONS:
• Review and reset expired passwords immediately
• Notify users with passwords expiring soon
• Consider implementing password policy reminders
• Monitor disabled accounts for cleanup
• Review accounts that never expire for security compliance
"""
        
        self.summary_text.setPlainText(report)
        
    def update_config_info(self):
        """Update configuration information display"""
        params = self.get_connection_params()
        
        config_info = f"""⚙️ ACTIVE DIRECTORY CONFIGURATION
{'=' * 40}

CONNECTION SETTINGS:
• Server: {params.get('server', 'Not configured')}
• Port: {params.get('port', 636)}
• SSL/TLS: {'Enabled' if params.get('use_ssl', True) else 'Disabled'}
• Domain: {params.get('domain', 'Not configured')}
• Base DN: {params.get('base_dn', 'Not configured')}
• Username: {params.get('username', 'Not configured')}
• Password: {'Set' if params.get('password') else 'Not set'}

APPLICATION SETTINGS:
• Auto Refresh: {'Enabled' if self.auto_refresh_check.isChecked() else 'Disabled'}
• Refresh Interval: {self.refresh_interval_spin.value()} seconds
• Warning Days: {self.warning_days_spin.value()} days

STATUS:
• Last Refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S') if self.users_data else 'Never'}
• Total Users Loaded: {len(self.users_data)}
• Connection Status: {'Connected' if self.users_data else 'Not connected'}

SECURITY NOTES:
• Passwords are never saved to configuration files
• SSL/TLS encryption is recommended for production use
• Service account should have minimal required permissions
• Monitor LDAP server logs for connection attempts
"""
        
        self.config_text.setPlainText(config_info)
        
    def save_configuration(self):
        """Save configuration to file"""
        try:
            config_dir = Path.home() / ".sigmatoolkit"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "ad_config.json"
            
            config_data = {
                "server": self.server_edit.text(),
                "port": self.port_spin.value(),
                "use_ssl": self.use_ssl_check.isChecked(),
                "domain": self.domain_edit.text(),
                "base_dn": self.base_dn_edit.text(),
                "username": self.username_edit.text(),
                "auto_refresh": self.auto_refresh_check.isChecked(),
                "refresh_interval": self.refresh_interval_spin.value(),
                "warning_days": self.warning_days_spin.value()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            self.success("✅ Configuration saved successfully")
            QMessageBox.information(self, "Configuration Saved", 
                                  f"Configuration saved to:\n{config_file}")
            
        except Exception as e:
            self.error(f"❌ Failed to save configuration: {str(e)}")
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{str(e)}")
            
    def load_configuration(self):
        """Load configuration from file"""
        try:
            config_dir = Path.home() / ".sigmatoolkit"
            config_file = config_dir / "ad_config.json"
            
            if not config_file.exists():
                QMessageBox.information(self, "No Configuration", 
                                      "No saved configuration found.")
                return
                
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                
            # Load configuration into UI
            self.server_edit.setText(config_data.get("server", ""))
            self.port_spin.setValue(config_data.get("port", 636))
            self.use_ssl_check.setChecked(config_data.get("use_ssl", True))
            self.domain_edit.setText(config_data.get("domain", ""))
            self.base_dn_edit.setText(config_data.get("base_dn", ""))
            self.username_edit.setText(config_data.get("username", ""))
            self.auto_refresh_check.setChecked(config_data.get("auto_refresh", False))
            self.refresh_interval_spin.setValue(config_data.get("refresh_interval", 300))
            self.warning_days_spin.setValue(config_data.get("warning_days", 14))
            
            self.success("✅ Configuration loaded successfully")
            QMessageBox.information(self, "Configuration Loaded", 
                                  "Configuration loaded successfully!")
            
        except Exception as e:
            self.error(f"❌ Failed to load configuration: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load configuration:\n{str(e)}")
            
    def export_data(self):
        """Export current data to CSV"""
        if not self.users_data:
            QMessageBox.information(self, "No Data", 
                                  "No data to export. Please refresh data first.")
            return
            
        try:
            export_dir = Path.home() / "Downloads"
            export_file = export_dir / f"ad_password_expiry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                f.write("Username,Display Name,Email,Days Until Expiry,Password Last Set,Password Expires,Status\n")
                
                for user in self.users_data:
                    username = user.get('username', '')
                    display_name = user.get('display_name', '')
                    email = user.get('email', '')
                    days = user.get('days_until_expiry', 0)
                    
                    # Format dates
                    last_set = user.get('password_last_set', '')
                    if isinstance(last_set, datetime):
                        last_set = last_set.strftime('%Y-%m-%d %H:%M')
                        
                    expires = user.get('password_expires', '')
                    if user.get('password_never_expires', False):
                        expires = "Never"
                    elif isinstance(expires, datetime):
                        expires = expires.strftime('%Y-%m-%d %H:%M')
                        
                    # Status
                    if user.get('account_disabled', False):
                        status = "Disabled"
                    elif user.get('password_never_expires', False):
                        status = "Never Expires"
                    elif days < 0:
                        status = "Expired"
                    elif days <= 7:
                        status = "Expiring Soon"
                    else:
                        status = "Active"
                        
                    # Write row
                    f.write(f'"{username}","{display_name}","{email}",{days},"{last_set}","{expires}","{status}"\n')
                    
            self.success(f"✅ Data exported to: {export_file}")
            QMessageBox.information(self, "Export Complete", 
                                  f"Data exported successfully to:\n{export_file}")
            
        except Exception as e:
            self.error(f"❌ Export failed: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")
            
    def toggle_auto_refresh(self, enabled):
        """Toggle auto refresh functionality"""
        if enabled:
            interval = self.refresh_interval_spin.value() * 1000  # Convert to milliseconds
            self.refresh_timer.start(interval)
            self.info(f"🔄 Auto refresh enabled - every {self.refresh_interval_spin.value()} seconds")
        else:
            self.refresh_timer.stop()
            self.info("⏸️ Auto refresh disabled")
            
    def closeEvent(self, event):
        """Handle tab close event"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()