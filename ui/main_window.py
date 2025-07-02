# ui/main_window.py - UPDATED WITH FOLDER PERMISSIONS ANALYZER v1.7.0
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

# Try to import the AD tab
try:
    from ad.ad_tab import ADPasswordTab
    AD_TAB_AVAILABLE = True
except ImportError:
    AD_TAB_AVAILABLE = False
    print("⚠️ AD Password Checker tab not available - create ad module first")

# Try to import the folder permissions tab
try:
    from file_folder_permissions.permissions_tab import PermissionsTab
    PERMISSIONS_TAB_AVAILABLE = True
except ImportError:
    PERMISSIONS_TAB_AVAILABLE = False
    print("⚠️ Folder Permissions tab not available - create file_folder_permissions module first")

# Try to import the port listener tab
try:
    from portlistener.port_listener_tab import PortListenerTab
    PORT_LISTENER_TAB_AVAILABLE = True
except ImportError:
    PORT_LISTENER_TAB_AVAILABLE = False
    print("⚠️ Port Listener tab not available - create portlistener module first")

# Try to import the mail tab, but handle gracefully if not available
try:
    from mail.mail_tab import MailTab
    MAIL_TAB_AVAILABLE = True
except ImportError:
    MAIL_TAB_AVAILABLE = False
    print("⚠️ Mail tab not available - run setup script first")

# Try to import the services tab, but handle gracefully if not available
try:
    from services.services_tab import ServiceMonitorTab
    SERVICES_TAB_AVAILABLE = True
except ImportError:
    SERVICES_TAB_AVAILABLE = False
    print("⚠️ Services tab not available - create services module first")

from core.logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Update version based on available features
        version_base = "1.7.0" if PERMISSIONS_TAB_AVAILABLE else ("1.6.0" if AD_TAB_AVAILABLE else ("1.5.0" if SERVICES_TAB_AVAILABLE else ("1.4.0" if MAIL_TAB_AVAILABLE else "1.3.0")))
        
        # Add sub-version indicators for additional features
        sub_features = []
        if PORT_LISTENER_TAB_AVAILABLE:
            sub_features.append("1")
        if len(sub_features) > 0:
            self.version = f"{version_base}.{'.'.join(sub_features)}"
        else:
            self.version = version_base
            
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
        
        # Add tabs in order of importance/usage
        
        # Add Service Monitor tab first (most important for infrastructure monitoring)
        if SERVICES_TAB_AVAILABLE:
            self.services_tab = ServiceMonitorTab(self.logger)
            self.tab_widget.addTab(self.services_tab, "🟢 Service Monitor")
        
        # Add AD Password Checker tab (high priority for security)
        if AD_TAB_AVAILABLE:
            self.ad_tab = ADPasswordTab(self.logger)
            self.tab_widget.addTab(self.ad_tab, "🔐 AD Password Checker")

        # Add Folder Permissions Analyzer tab (NEW - security compliance)
        if PERMISSIONS_TAB_AVAILABLE:
            self.permissions_tab = PermissionsTab(self.logger)
            self.tab_widget.addTab(self.permissions_tab, "📁 Folder Permissions")
             
        # Add Network tab
        self.network_tab = NetworkTab(self.logger)
        self.tab_widget.addTab(self.network_tab, "🌐 Network Testing")
        
        # Add DNS tab
        self.dns_tab = DNSTab(self.logger)
        self.tab_widget.addTab(self.dns_tab, "🔍 DNS Testing")
        
        # Add SMTP tab
        self.smtp_tab = SMTPTab(self.logger)
        self.tab_widget.addTab(self.smtp_tab, "📧 SMTP Testing")
        
        # Add Port Listener tab
        if PORT_LISTENER_TAB_AVAILABLE:
            self.port_listener_tab = PortListenerTab(self.logger)
            self.tab_widget.addTab(self.port_listener_tab, "🔌 Port Listener")
        
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
        
        # Add export buttons for different modules
        if SERVICES_TAB_AVAILABLE:
            self.export_services_btn = QPushButton("Export Service Report")
            controls_layout.addWidget(self.export_services_btn)
            
        if AD_TAB_AVAILABLE:
            self.export_ad_btn = QPushButton("Export AD Report")
            controls_layout.addWidget(self.export_ad_btn)

        if PERMISSIONS_TAB_AVAILABLE:
            self.export_permissions_btn = QPushButton("Export Permissions Report")
            controls_layout.addWidget(self.export_permissions_btn)
        
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
        
        if SERVICES_TAB_AVAILABLE:
            self.export_services_btn.setStyleSheet(button_style)
            
        if AD_TAB_AVAILABLE:
            self.export_ad_btn.setStyleSheet(button_style)

        if PERMISSIONS_TAB_AVAILABLE:
            self.export_permissions_btn.setStyleSheet(button_style)
        
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
        
        if PERMISSIONS_TAB_AVAILABLE:
            self.logger.info("📁 NEW: Folder Permissions Analyzer for NTFS security compliance")
            self.logger.info("🔐 Analyze AD groups, scan network shares, and audit folder access permissions")
        
        if AD_TAB_AVAILABLE:
            self.logger.info("🔐 AD Password Checker for Active Directory security compliance")
            self.logger.info("🛡️ Monitor password expiry, enforce policies, and maintain security standards")
        
        if PORT_LISTENER_TAB_AVAILABLE:
            self.logger.info("🔌 Port Listener for firewall testing and connection monitoring")
        
        if SERVICES_TAB_AVAILABLE:
            self.logger.info("🟢 Service Monitor: Microsoft 365, cloud services, and custom monitoring")
        
        if MAIL_TAB_AVAILABLE:
            self.logger.info("📨 Mail Header Analysis: SPF/DKIM/DMARC, delivery paths, and spam detection")
        else:
            self.logger.warning("📨 Mail Analysis tab not available")
            
        # Update toolkit description based on available features
        toolkit_description = "🔍 Complete toolkit: "
        tabs = []
        
        if SERVICES_TAB_AVAILABLE:
            tabs.append("Service Monitor")
        if AD_TAB_AVAILABLE:
            tabs.append("AD Security")
        if PERMISSIONS_TAB_AVAILABLE:
            tabs.append("Folder Permissions")
        tabs.extend(["Network", "DNS", "SMTP"])
        if PORT_LISTENER_TAB_AVAILABLE:
            tabs.append("Port Listener")
        tabs.append("Speed")
        if MAIL_TAB_AVAILABLE:
            tabs.append("Mail")
            
        toolkit_description += " → ".join(tabs)
        self.logger.info(toolkit_description)
            
        self.logger.info("💡 Ready for comprehensive IT infrastructure monitoring, security compliance, and testing!")
        
    def setup_connections(self):
        self.clear_btn.clicked.connect(self.clear_output)
        self.copy_btn.clicked.connect(self.copy_output)
        self.debug_btn.toggled.connect(self.toggle_debug)
        
        if SERVICES_TAB_AVAILABLE:
            self.export_services_btn.clicked.connect(self.export_service_report)
            
        if AD_TAB_AVAILABLE:
            self.export_ad_btn.clicked.connect(self.export_ad_report)

        if PERMISSIONS_TAB_AVAILABLE:
            self.export_permissions_btn.clicked.connect(self.export_permissions_report)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        if SERVICES_TAB_AVAILABLE:
            load_services_action = QAction('Load Service Config', self)
            load_services_action.triggered.connect(self.load_service_config)
            file_menu.addAction(load_services_action)
            
            save_services_action = QAction('Save Service Config', self)
            save_services_action.triggered.connect(self.save_service_config)
            file_menu.addAction(save_services_action)
            
            file_menu.addSeparator()
            
        if AD_TAB_AVAILABLE:
            load_ad_action = QAction('Load AD Config', self)
            load_ad_action.triggered.connect(self.load_ad_config)
            file_menu.addAction(load_ad_action)
            
            save_ad_action = QAction('Save AD Config', self)
            save_ad_action.triggered.connect(self.save_ad_config)
            file_menu.addAction(save_ad_action)
            
            file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        if SERVICES_TAB_AVAILABLE:
            service_monitor_action = QAction('Service Monitor', self)
            tab_index = 0  # Services is first tab
            service_monitor_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(tab_index))
            tools_menu.addAction(service_monitor_action)
            tools_menu.addSeparator()
            
        if AD_TAB_AVAILABLE:
            ad_password_action = QAction('AD Password Checker', self)
            tab_index = 1 if SERVICES_TAB_AVAILABLE else 0
            ad_password_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(tab_index))
            tools_menu.addAction(ad_password_action)
            tools_menu.addSeparator()

        if PERMISSIONS_TAB_AVAILABLE:
            permissions_action = QAction('Folder Permissions Analyzer', self)
            tab_index = 0
            if SERVICES_TAB_AVAILABLE:
                tab_index += 1
            if AD_TAB_AVAILABLE:
                tab_index += 1
            permissions_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(tab_index))
            tools_menu.addAction(permissions_action)
            tools_menu.addSeparator()
        
        # Add Port Listener menu item
        if PORT_LISTENER_TAB_AVAILABLE:
            port_listener_action = QAction('Port Listener', self)
            # Calculate the correct tab index based on available tabs
            tab_index = 3  # Default position after Network, DNS, SMTP
            if SERVICES_TAB_AVAILABLE:
                tab_index += 1
            if AD_TAB_AVAILABLE:
                tab_index += 1
            if PERMISSIONS_TAB_AVAILABLE:
                tab_index += 1
            port_listener_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(tab_index))
            tools_menu.addAction(port_listener_action)
            tools_menu.addSeparator()
        
        if MAIL_TAB_AVAILABLE:
            mail_analysis_action = QAction('Mail Header Analysis', self)
            # Calculate correct tab index for mail tab (last tab)
            tab_index = self.tab_widget.count() - 1
            mail_analysis_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(tab_index))
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
        
        if AD_TAB_AVAILABLE:
            ad_help_action = QAction('AD Password Checker Help', self)
            ad_help_action.triggered.connect(self.show_ad_help)
            help_menu.addAction(ad_help_action)

        if PERMISSIONS_TAB_AVAILABLE:
            permissions_help_action = QAction('Folder Permissions Help', self)
            permissions_help_action.triggered.connect(self.show_permissions_help)
            help_menu.addAction(permissions_help_action)
        
        if PORT_LISTENER_TAB_AVAILABLE:
            port_help_action = QAction('Port Listener Help', self)
            port_help_action.triggered.connect(self.show_port_listener_help)
            help_menu.addAction(port_help_action)
        
        if SERVICES_TAB_AVAILABLE:
            service_help_action = QAction('Service Monitor Help', self)
            service_help_action.triggered.connect(self.show_service_help)
            help_menu.addAction(service_help_action)
        
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
        
    def export_service_report(self):
        """Export service monitoring report"""
        if not SERVICES_TAB_AVAILABLE:
            return
            
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Service Report", 
                f"service_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                success = self.services_tab.services_tools.export_status_report(file_path)
                if success:
                    self.logger.success(f"Service report exported to: {file_path}")
                else:
                    self.logger.error("Failed to export service report")
                    
        except Exception as e:
            self.logger.error(f"Export service report failed: {str(e)}")
            
    def export_ad_report(self):
        """Export AD password report"""
        if not AD_TAB_AVAILABLE:
            return
            
        try:
            if not self.ad_tab.users_data:
                QMessageBox.information(self, "No Data", "No AD data to export. Please refresh AD data first.")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export AD Password Report", 
                f"ad_password_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Use the AD tab's export functionality
                self.ad_tab.export_data()
                self.logger.success(f"AD password report exported")
                    
        except Exception as e:
            self.logger.error(f"Export AD report failed: {str(e)}")

    def export_permissions_report(self):
        """Export folder permissions report"""
        if not PERMISSIONS_TAB_AVAILABLE:
            return
            
        try:
            if not self.permissions_tab.permissions_data:
                QMessageBox.information(self, "No Data", "No permissions data to export. Please run a folder scan first.")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Folder Permissions Report", 
                f"folder_permissions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                if file_path.lower().endswith('.json'):
                    success = self.permissions_tab.permissions_tools.export_to_json(
                        self.permissions_tab.permissions_data, file_path)
                else:
                    success = self.permissions_tab.permissions_tools.export_to_csv(
                        self.permissions_tab.permissions_data, file_path)
                
                if success:
                    self.logger.success(f"Folder permissions report exported to: {file_path}")
                else:
                    self.logger.error("Failed to export permissions report")
                    
        except Exception as e:
            self.logger.error(f"Export permissions report failed: {str(e)}")
            
    def load_service_config(self):
        """Load service configuration from file"""
        if not SERVICES_TAB_AVAILABLE:
            return
            
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Service Configuration",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                success = self.services_tab.services_tools.load_services_from_config(file_path)
                if success:
                    self.services_tab.update_service_tree()
                    self.logger.success(f"Service configuration loaded from: {file_path}")
                else:
                    self.logger.error("Failed to load service configuration")
                    
        except Exception as e:
            self.logger.error(f"Load service config failed: {str(e)}")
            
    def save_service_config(self):
        """Save current service configuration to file"""
        if not SERVICES_TAB_AVAILABLE:
            return
            
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Service Configuration",
                f"service_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                success = self.services_tab.services_tools.save_services_to_config(file_path)
                if success:
                    self.logger.success(f"Service configuration saved to: {file_path}")
                else:
                    self.logger.error("Failed to save service configuration")
                    
        except Exception as e:
            self.logger.error(f"Save service config failed: {str(e)}")
            
    def load_ad_config(self):
        """Load AD configuration from file"""
        if not AD_TAB_AVAILABLE:
            return
            
        try:
            self.ad_tab.load_configuration()
        except Exception as e:
            self.logger.error(f"Load AD config failed: {str(e)}")
            
    def save_ad_config(self):
        """Save AD configuration to file"""
        if not AD_TAB_AVAILABLE:
            return
            
        try:
            self.ad_tab.save_configuration()
        except Exception as e:
            self.logger.error(f"Save AD config failed: {str(e)}")
        
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
                    
                    # Export service status if available
                    if SERVICES_TAB_AVAILABLE:
                        f.write("SERVICE STATUS SUMMARY:\n")
                        f.write("-" * 25 + "\n")
                        summary = self.services_tab.services_tools.get_status_summary()
                        f.write(f"Total Services: {summary['total']}\n")
                        f.write(f"Healthy: {summary['healthy']}\n")
                        f.write(f"Warning: {summary['warning']}\n")
                        f.write(f"Critical: {summary['critical']}\n\n")
                        
                    # Export AD status if available
                    if AD_TAB_AVAILABLE and self.ad_tab.users_data:
                        f.write("AD PASSWORD STATUS SUMMARY:\n")
                        f.write("-" * 30 + "\n")
                        summary = self.ad_tab.ad_tools.get_status_summary(self.ad_tab.users_data)
                        f.write(f"Total Users: {summary['total']}\n")
                        f.write(f"Expired: {summary['expired']}\n")
                        f.write(f"Expiring Soon: {summary['expiring_soon']}\n")
                        f.write(f"Active: {summary['active']}\n")
                        f.write(f"Never Expires: {summary['never_expires']}\n")
                        f.write(f"Disabled: {summary['disabled']}\n\n")

                    # Export permissions status if available
                    if PERMISSIONS_TAB_AVAILABLE and self.permissions_tab.permissions_data:
                        f.write("FOLDER PERMISSIONS SUMMARY:\n")
                        f.write("-" * 30 + "\n")
                        stats = self.permissions_tab.permissions_tools.get_summary_stats(
                            self.permissions_tab.permissions_data)
                        f.write(f"Total Entries: {stats['total_entries']}\n")
                        f.write(f"Unique Paths: {stats['unique_paths']}\n")
                        f.write(f"Unique Identities: {stats['unique_identities']}\n")
                        f.write(f"AD Groups: {stats['ad_groups']}\n")
                        f.write(f"Inherited Permissions: {stats['inherited_permissions']}\n")
                        f.write(f"Explicit Permissions: {stats['explicit_permissions']}\n")
                        f.write(f"Deny Permissions: {stats['deny_permissions']}\n\n")
                    
                    # Export port listener stats if available
                    if PORT_LISTENER_TAB_AVAILABLE and hasattr(self, 'port_listener_tab'):
                        if self.port_listener_tab.is_listening:
                            f.write("PORT LISTENER STATUS:\n")
                            f.write("-" * 20 + "\n")
                            stats = self.port_listener_tab.port_tools.get_statistics()
                            f.write(f"Status: Active\n")
                            f.write(f"Connections: {stats['connections']}\n")
                            f.write(f"Last Client: {stats.get('last_client', 'None')}\n")
                            f.write(f"Uptime: {stats['uptime']}\n\n")
                    
                    # Export output log
                    f.write("CONSOLE OUTPUT:\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.output_text.toPlainText())
                    f.write("\n\n")
                    
                self.logger.success(f"All results exported to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
        
    def show_about(self):
        features_text = """• Folder Permissions Analyzer (NTFS Security, AD Groups, UNC Network Shares, Permission Auditing)
• AD Password Checker (Active Directory Security, Password Expiry Monitoring, Compliance Reporting)
• Service Monitor (Microsoft 365, Google Workspace, AWS, Azure, Custom Services)
• Network Testing (Ping, Traceroute, Port Scan)
• DNS Testing (Forward/Reverse, MX, SPF, TXT, NS, CNAME, AAAA)
• SMTP Testing (Connection, Auth, Email Sending, MX Validation)
• Speed Testing (Internet, LAN, Latency, Real-time Monitoring)"""

        if PORT_LISTENER_TAB_AVAILABLE:
            features_text += """
• Port Listener (Firewall Testing, Connection Monitoring, Network Validation)"""

        if MAIL_TAB_AVAILABLE:
            features_text += """
• Mail Analysis (Header Analysis, SPF/DKIM/DMARC, Delivery Path, Spam Detection)"""

        features_text += """
• Debug logging and easy result copying"""

        version_history = """v1.7.0 - Added comprehensive folder permissions analyzer for NTFS security auditing
v1.6.0 - Added comprehensive Active Directory password expiry monitoring and security compliance
v1.5.1 - Added Port Listener for firewall testing and connection monitoring
v1.5.0 - Added comprehensive service monitoring with Microsoft 365, cloud providers, and custom services
v1.4.0 - Added comprehensive mail header analysis and email authentication
v1.3.0 - Added comprehensive speed testing with real-time displays
v1.2.0 - Added SMTP testing capabilities
v1.1.0 - Added DNS testing capabilities
v1.0.0 - Initial release with network tools"""

        # Filter version history based on available features
        if not PERMISSIONS_TAB_AVAILABLE:
            version_history = version_history.replace("v1.7.0 - Added comprehensive folder permissions analyzer for NTFS security auditing\n", "")

        if not AD_TAB_AVAILABLE:
            version_history = version_history.replace("v1.6.0 - Added comprehensive Active Directory password expiry monitoring and security compliance\n", "")

        if not PORT_LISTENER_TAB_AVAILABLE:
            version_history = version_history.replace("v1.5.1 - Added Port Listener for firewall testing and connection monitoring\n", "")

        if not SERVICES_TAB_AVAILABLE:
            version_history = version_history.replace("v1.5.0 - Added comprehensive service monitoring with Microsoft 365, cloud providers, and custom services\n", "")

        if not MAIL_TAB_AVAILABLE:
            version_history = version_history.replace("v1.4.0 - Added comprehensive mail header analysis and email authentication\n", "")

        QMessageBox.about(self, "About SigmaToolkit", 
                         f"SigmaToolkit v{self.version}\n\n"
                         "Sigma's IT Swiss Army Knife\n"
                         "A comprehensive tool for system administrators\n"
                         "to perform infrastructure monitoring, security compliance, network, DNS, email, speed, and mail diagnostics.\n\n"
                         f"Features:\n{features_text}\n\n"
                         f"Version History:\n{version_history}\n\n"
                         "Created for efficient IT troubleshooting, security compliance, and infrastructure monitoring workflows.")
    
    def show_permissions_help(self):
        """Show help for folder permissions analyzer features"""
        if not PERMISSIONS_TAB_AVAILABLE:
            QMessageBox.information(self, "Folder Permissions Analyzer Not Available", 
                                  "The Folder Permissions Analyzer feature is not currently available.\n\n"
                                  "To enable this feature:\n"
                                  "1. Create the file_folder_permissions module directory\n"
                                  "2. Add the permissions_tab.py and permissions_tools.py files\n"
                                  "3. Restart SigmaToolkit\n\n"
                                  "The Folder Permissions Analyzer provides comprehensive NTFS "
                                  "permissions analysis and Active Directory security auditing.")
            return
            
        help_text = """📁 FOLDER PERMISSIONS ANALYZER HELP

The Folder Permissions Analyzer provides comprehensive NTFS permissions analysis and Active Directory security auditing:

🔍 PERMISSION SCANNING:
• Scan local folders and UNC network paths (\\\\server\\share\\folder)
• Recursive subfolder scanning with progress tracking
• Focus on directory permissions only (excludes files for performance)
• Support for both standard and complex folder structures
• Real-time scanning progress with detailed status updates

👥 ACTIVE DIRECTORY INTEGRATION:
• Automatically identifies AD groups vs local users with smart detection
• Filter to show only Active Directory groups for security focus
• Displays user-friendly permission types: Read, Write, Change, Delete, List
• Shows inheritance status and Allow/Deny access types
• Clean permission display with relevant security information

📊 COMPREHENSIVE ANALYSIS:
• Shows only relevant permission types for security auditing
• Indicates inheritance status for compliance reporting
• Real-time filtering and search capabilities across all data
• Sortable columns for efficient data analysis
• Permission summary statistics and reporting

📤 FLEXIBLE EXPORT OPTIONS:
• Export All to CSV: Complete scan results for compliance documentation
• Export Selected to CSV: Export only selected table rows for focused analysis
• Export to JSON: Machine-readable format for automation and integration
• Timestamped filenames for easy organization and audit trails

🎨 PROFESSIONAL INTERFACE:
• Clean, modern interface designed for security professionals
• Resizable columns with helpful tooltips for efficient workflow
• Progress indication during scans with real-time status updates
• Color-coded status updates and comprehensive error handling

🔧 SCANNING CAPABILITIES:
• Local Paths: C:\\Users\\Public\\Documents, C:\\Data\\Shares
• UNC Network Paths: \\\\fileserver\\departments\\IT, \\\\nas\\backups
• Mixed environments: Seamlessly handle both local and network storage
• Large scale: Efficiently process thousands of folders and permissions

📋 PERMISSION TYPES EXPLAINED:
• Read: View folder contents and file properties
• Write: Create new files and folders
• Change: Modify existing files and folders (includes Write)
• Delete: Remove files and folders
• List: Browse folder contents and traverse directories

🔐 SECURITY ANALYSIS:
• Full Control → Displays as: "Read, Write, Change, Delete, List"
• Modify → Displays as: "Read, Write, Change, Delete, List"
• Read & Execute → Displays as: "Read, List"
• Custom Permissions: Shows exact permission combinations

🛠️ FILTERING & SEARCH:
• Search Filter: Filter by identity name, path, or permission type
• AD Groups Filter: Show only domain groups, hide local users
• Real-time filtering: Instant results as you type
• Column sorting: Click headers to sort by any column

💡 BEST PRACTICES:
• Start with root network shares for comprehensive auditing
• Use "Show AD Groups Only" to focus on domain security
• Export results regularly for compliance documentation
• Run as Administrator for full access to all folders
• Scan during off-peak hours for large network shares

🔒 SECURITY CONSIDERATIONS:
• Application requires read access to folder ACLs only
• No modifications are made to any permissions or security settings
• Network credentials use current user context for authentication
• Export files contain sensitive permission information - handle securely

⚙️ TROUBLESHOOTING:
• "No Permissions Found": Run as Administrator or check path accessibility
• "Path Syntax Error": Use proper Windows format (C:\\folder or \\\\server\\share)
• Slow Scanning: Disable subfolders for faster scanning or scan specific subdirectories
• Network Issues: Verify network connectivity and credentials for UNC paths

🎯 USE CASES:
• Security Auditing: Identify overprivileged accounts and excessive permissions
• Compliance Reporting: Generate documentation for SOX, HIPAA, PCI-DSS audits
• Access Reviews: Regular review of folder access for least privilege principles
• Migration Planning: Document current permissions before system migrations
• Incident Response: Quickly identify who has access to compromised folders"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Folder Permissions Analyzer Help")
        msg.setText("Folder Permissions Analyzer Help")
        msg.setDetailedText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def show_ad_help(self):
        """Show help for AD Password Checker features"""
        if not AD_TAB_AVAILABLE:
            QMessageBox.information(self, "AD Password Checker Not Available", 
                                  "The AD Password Checker feature is not currently available.\n\n"
                                  "To enable this feature:\n"
                                  "1. Create the ad module directory\n"
                                  "2. Add the ad_tab.py and ad_tools.py files\n"
                                  "3. Install required dependencies: pip install ldap3 pycryptodome\n"
                                  "4. Restart SigmaToolkit\n\n"
                                  "The AD Password Checker provides comprehensive Active Directory "
                                  "password monitoring and security compliance features.")
            return
            
        help_text = """🔐 AD PASSWORD CHECKER HELP

The AD Password Checker provides comprehensive Active Directory password monitoring and security compliance:

🛡️ SECURITY FEATURES:
• LDAP over SSL/TLS (LDAPS) with strong cipher suites
• NTLM authentication for Windows Active Directory
• Certificate validation for secure connections
• No sensitive data storage - passwords never saved to config files
• Multiple authentication methods with automatic fallback

📊 PASSWORD MONITORING:
• Real-time password expiration tracking with exact day counts
• Visual indicators for expired (red) and expiring soon (yellow) passwords
• Handles special cases: "Password never expires" and disabled accounts
• Sortable data table with comprehensive user information
• Auto-refresh capability with configurable intervals

🔧 CONFIGURATION:
• Server: Your AD domain controller (dc01.company.com)
• Port: 636 (SSL) or 389 (non-SSL) - SSL recommended
• Domain: Your Windows domain name (COMPANY)
• Base DN: LDAP search base (DC=company,DC=com)
• Service Account: AD account with read permissions

📈 MONITORING DASHBOARD:
• 🔴 Expired Passwords: Immediate attention required
• 🟡 Expiring Soon: Passwords expiring within 7 days
• ✅ Active: Passwords in good standing
• ♾️ Never Expires: Accounts with non-expiring passwords
• ❌ Disabled: Disabled user accounts

📋 REPORTING FEATURES:
• Summary Report: Comprehensive password status overview
• Export to CSV: Detailed user data for external analysis
• Configuration Management: Save/load AD connection settings
• Status Dashboards: Real-time monitoring displays

🛠️ INTEGRATION CAPABILITIES:
• Standalone application for immediate use
• API class for integration with existing applications
• Clean OOP structure for maintainability
• Threaded operations to prevent UI blocking

💡 BEST PRACTICES:
• Use dedicated service account with minimal permissions
• Always use SSL/TLS (port 636) in production environments
• Monitor expired passwords daily
• Set up auto-refresh for continuous monitoring
• Export reports for compliance documentation
• Review accounts that never expire for security compliance

🔒 SECURITY REQUIREMENTS:
• Service account needs read access to user objects
• No administrator privileges required
• Network access to AD domain controller
• Firewall rules allowing LDAP/LDAPS traffic

⚙️ TROUBLESHOOTING:
• Test connection before first use
• Verify service account credentials
• Check network connectivity to domain controller
• Ensure proper Base DN configuration
• Monitor LDAP server logs for authentication issues"""
        
        msg = QMessageBox()
        msg.setWindowTitle("AD Password Checker Help")
        msg.setText("AD Password Checker Help")
        msg.setDetailedText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def show_port_listener_help(self):
        """Show help for port listener features"""
        if not PORT_LISTENER_TAB_AVAILABLE:
            QMessageBox.information(self, "Port Listener Not Available", 
                                  "The Port Listener feature is not currently available.\n\n"
                                  "To enable this feature:\n"
                                  "1. Create the portlistener module directory\n"
                                  "2. Add the port_listener_tab.py and port_listener_tools.py files\n"
                                  "3. Restart SigmaToolkit\n\n"
                                  "The Port Listener provides firewall testing and connection monitoring.")
            return
            
        help_text = """🔌 PORT LISTENER HELP

The Port Listener tab provides comprehensive firewall testing and connection monitoring:

🔧 CONFIGURATION:
• IP Address: Use 0.0.0.0 for all interfaces or specific IP
• Port: Any port 1-65535 (ports < 1024 require admin privileges)
• Response Type: HTTP OK, Echo, or Silent modes

⚠️ FIREWALL REQUIREMENTS:
• Windows Firewall must allow inbound connections on the specified port
• Administrator privileges required for ports below 1024
• Create firewall rules or temporarily disable firewall for testing

🎮 OPERATION:
• Start/Stop: Toggle listening state with real-time status
• Test Connection: Verify connectivity to your own listener
• Connection Log: Monitor all incoming connections with timestamps

📊 MONITORING:
• Real-time connection counting and client tracking
• Uptime monitoring with precise timing
• Last client IP and connection statistics

🔍 RESPONSE TYPES:
• HTTP OK: Sends HTTP 200 response (web-compatible)
• Echo: Returns received data back to client
• Silent: Accepts connections but sends no response

🧪 TESTING:
• Use telnet: telnet your-server-ip port-number
• Use curl: curl http://your-server-ip:port-number
• Use browser for HTTP responses
• Check with nmap or other port scanners

💡 USE CASES:
• Test firewall rules and port accessibility
• Verify network connectivity through corporate firewalls
• Monitor unauthorized connection attempts
• Validate load balancer and reverse proxy configurations
• Debug network infrastructure issues

🛡️ SECURITY:
• Monitor who's connecting to your test ports
• Detect port scanning and unauthorized access attempts
• Use for penetration testing and security assessments"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Port Listener Help")
        msg.setText("Port Listener Help")
        msg.setDetailedText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def show_service_help(self):
        """Show help for service monitoring features"""
        if not SERVICES_TAB_AVAILABLE:
            QMessageBox.information(self, "Service Monitor Not Available", 
                                  "The Service Monitor feature is not currently available.\n\n"
                                  "To enable this feature:\n"
                                  "1. Create the services module directory\n"
                                  "2. Add the services_tab.py and services_tools.py files\n"
                                  "3. Restart SigmaToolkit\n\n"
                                  "The Service Monitor provides real-time monitoring of Microsoft 365, "
                                  "cloud services, and custom endpoints.")
            return
            
        help_text = """🟢 SERVICE MONITOR HELP

The Service Monitor tab provides comprehensive infrastructure monitoring:

📊 SERVICE STATUS OVERVIEW:
• Real-time status monitoring with color-coded indicators
• Response time tracking and performance monitoring
• Auto-refresh capability for continuous monitoring
• Organized by service categories for easy management

🔄 MONITORING CAPABILITIES:
• HTTP/HTTPS: Web services and APIs (200 OK status)
• Ping Test: Basic connectivity testing
• Port Check: Specific port availability
• DNS Resolution: Domain name resolution testing
• Custom API: Advanced API endpoint monitoring

☁️ PRE-CONFIGURED SERVICES:
• Microsoft 365: Exchange, SharePoint, Teams, OneDrive
• Google Workspace: Gmail, Drive, Meet, Calendar
• Cloud Providers: AWS, Azure, Google Cloud, Cloudflare
• One-click addition of entire service categories

🔧 CUSTOM SERVICE MANAGEMENT:
• Add any HTTP endpoint, server, or service
• Configure different check types for specific needs
• Organize services into custom categories
• Test configurations before adding to monitoring

📈 STATUS SUMMARY:
• 🟢 Healthy: Service responding normally (< 200ms)
• 🟡 Warning: Service slow or minor issues (200-1000ms)
• 🔴 Critical: Service down or major issues (> 1000ms or failed)

💾 CONFIGURATION MANAGEMENT:
• Save/Load service configurations
• Export status reports for documentation
• Bulk service management capabilities

💡 BEST PRACTICES:
• Start with Microsoft 365 services if you use them
• Add critical infrastructure services first
• Use auto-refresh for continuous monitoring
• Export reports for incident documentation
• Test custom services before adding to monitoring"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Service Monitor Help")
        msg.setText("Service Monitor Help")
        msg.setDetailedText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
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