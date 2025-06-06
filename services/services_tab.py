# services/services_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QGridLayout,
                            QComboBox, QCheckBox, QTreeWidget, QTreeWidgetItem,
                            QProgressBar, QFrame, QTextEdit, QSplitter,
                            QMessageBox, QInputDialog, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from core.base_tab import BaseTab
from services.services_tools import ServicesTools
import json

class ServiceMonitorTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.services_tools = ServicesTools(logger)
        self.auto_refresh_timer = QTimer()
        self.init_ui()
        self.setup_connections()
        self.load_default_services()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Service Status Overview Section
        overview_group = QGroupBox("🟢 Service Status Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh All")
        self.auto_refresh_cb = QCheckBox("Auto-refresh (30s)")
        self.add_service_btn = QPushButton("➕ Add Service")
        self.edit_service_btn = QPushButton("✏️ Edit Service")
        self.remove_service_btn = QPushButton("🗑️ Remove Service")
        
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.auto_refresh_cb)
        control_layout.addStretch()
        control_layout.addWidget(self.add_service_btn)
        control_layout.addWidget(self.edit_service_btn)
        control_layout.addWidget(self.remove_service_btn)
        
        overview_layout.addLayout(control_layout)
        
        # Service status tree
        self.service_tree = QTreeWidget()
        self.service_tree.setHeaderLabels([
            "Service", "Status", "Response Time", "Last Checked", "Details"
        ])
        self.service_tree.setMinimumHeight(300)
        
        # Style the tree
        self.service_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #e9ecef;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
        overview_layout.addWidget(self.service_tree)
        
        layout.addWidget(overview_group)
        
        # Service Categories Section
        categories_group = QGroupBox("📊 Service Categories")
        categories_layout = QHBoxLayout(categories_group)
        
        # Microsoft 365 Category
        ms365_frame = self.create_category_frame("Microsoft 365", [
            {"name": "Exchange Online", "url": "https://outlook.office365.com"},
            {"name": "SharePoint Online", "url": "https://login.microsoftonline.com"},
            {"name": "Teams", "url": "https://teams.microsoft.com"},
            {"name": "OneDrive", "url": "https://onedrive.live.com"}
        ])
        
        # Google Workspace Category
        google_frame = self.create_category_frame("Google Workspace", [
            {"name": "Gmail", "url": "https://mail.google.com"},
            {"name": "Google Drive", "url": "https://drive.google.com"},
            {"name": "Google Meet", "url": "https://meet.google.com"},
            {"name": "Google Calendar", "url": "https://calendar.google.com"}
        ])
        
        # Cloud Providers Category
        cloud_frame = self.create_category_frame("Cloud Providers", [
            {"name": "AWS Console", "url": "https://console.aws.amazon.com"},
            {"name": "Azure Portal", "url": "https://portal.azure.com"},
            {"name": "Google Cloud", "url": "https://console.cloud.google.com"},
            {"name": "Cloudflare", "url": "https://dash.cloudflare.com"}
        ])
        
        categories_layout.addWidget(ms365_frame)
        categories_layout.addWidget(google_frame)
        categories_layout.addWidget(cloud_frame)
        categories_layout.addStretch()
        
        layout.addWidget(categories_group)
        
        # Custom Services Section
        custom_group = QGroupBox("🔧 Custom Service Management")
        custom_layout = QGridLayout(custom_group)
        
        custom_layout.addWidget(QLabel("Service Name:"), 0, 0)
        self.service_name_edit = QLineEdit()
        self.service_name_edit.setPlaceholderText("My Custom Service")
        custom_layout.addWidget(self.service_name_edit, 0, 1)
        
        custom_layout.addWidget(QLabel("URL/Endpoint:"), 0, 2)
        self.service_url_edit = QLineEdit()
        self.service_url_edit.setPlaceholderText("https://example.com/api/health")
        custom_layout.addWidget(self.service_url_edit, 0, 3)
        
        custom_layout.addWidget(QLabel("Check Type:"), 1, 0)
        self.check_type_combo = QComboBox()
        self.check_type_combo.addItems([
            "HTTP Status (200 OK)",
            "Ping Test",
            "Port Check",
            "DNS Resolution",
            "Custom API Response"
        ])
        custom_layout.addWidget(self.check_type_combo, 1, 1)
        
        custom_layout.addWidget(QLabel("Category:"), 1, 2)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([
            "Custom Services",
            "Internal Tools",
            "External APIs",
            "Infrastructure",
            "Monitoring"
        ])
        custom_layout.addWidget(self.category_combo, 1, 3)
        
        self.add_custom_btn = QPushButton("➕ Add Custom Service")
        self.test_custom_btn = QPushButton("🧪 Test Service")
        
        custom_layout.addWidget(self.add_custom_btn, 2, 0, 1, 2)
        custom_layout.addWidget(self.test_custom_btn, 2, 2, 1, 2)
        
        layout.addWidget(custom_group)
        
        # Status Summary Section
        summary_group = QGroupBox("📈 Status Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        # Status indicators
        self.total_services_label = QLabel("Total Services: 0")
        self.healthy_services_label = QLabel("🟢 Healthy: 0")
        self.warning_services_label = QLabel("🟡 Warning: 0")
        self.critical_services_label = QLabel("🔴 Critical: 0")
        
        for label in [self.total_services_label, self.healthy_services_label, 
                     self.warning_services_label, self.critical_services_label]:
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px; margin: 2px;")
        
        self.healthy_services_label.setStyleSheet(
            "padding: 8px; border: 2px solid #28a745; border-radius: 4px; "
            "background-color: #d4edda; color: #155724; font-weight: bold;"
        )
        self.warning_services_label.setStyleSheet(
            "padding: 8px; border: 2px solid #ffc107; border-radius: 4px; "
            "background-color: #fff3cd; color: #856404; font-weight: bold;"
        )
        self.critical_services_label.setStyleSheet(
            "padding: 8px; border: 2px solid #dc3545; border-radius: 4px; "
            "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        )
        
        summary_layout.addWidget(self.total_services_label)
        summary_layout.addWidget(self.healthy_services_label)
        summary_layout.addWidget(self.warning_services_label)
        summary_layout.addWidget(self.critical_services_label)
        summary_layout.addStretch()
        
        layout.addWidget(summary_group)
        
        # Service Monitor Guide
        guide_group = QGroupBox("💡 Service Monitoring Guide")
        guide_layout = QVBoxLayout(guide_group)
        
        guide_text = QTextEdit()
        guide_text.setMaximumHeight(80)
        guide_text.setReadOnly(True)
        guide_text.setText(
            "Service Monitoring Tips:\n"
            "• Add custom services with specific health check endpoints\n"
            "• Use auto-refresh for continuous monitoring • Check response times for performance issues\n"
            "• Configure different check types (HTTP, Ping, Port, DNS) • Export status reports for documentation"
        )
        guide_layout.addWidget(guide_text)
        
        layout.addWidget(guide_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Style the buttons
        self.style_buttons()
        
    def create_category_frame(self, category_name, services):
        """Create a frame for a service category"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Category header
        header = QLabel(f"📁 {category_name}")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setStyleSheet("color: #0078d4; padding: 4px;")
        layout.addWidget(header)
        
        # Service buttons
        for service in services:
            btn = QPushButton(f"🔗 {service['name']}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 6px 10px;
                    margin: 2px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #0078d4;
                }
            """)
            btn.clicked.connect(
                lambda checked, name=service['name'], url=service['url']: 
                self.quick_add_service(name, url, category_name)
            )
            layout.addWidget(btn)
        
        # Quick add all button
        add_all_btn = QPushButton(f"➕ Add All {category_name}")
        add_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        add_all_btn.clicked.connect(
            lambda: self.add_category_services(category_name, services)
        )
        layout.addWidget(add_all_btn)
        
        return frame
        
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
        
        # Management buttons
        management_button_style = """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """
        
        # Apply styles
        for btn in [self.refresh_btn, self.add_custom_btn, self.test_custom_btn]:
            btn.setStyleSheet(main_button_style)
            
        for btn in [self.add_service_btn, self.edit_service_btn, self.remove_service_btn]:
            btn.setStyleSheet(management_button_style)
        
    def setup_connections(self):
        # Main control connections
        self.refresh_btn.clicked.connect(self.refresh_all_services)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        self.add_service_btn.clicked.connect(self.add_service_dialog)
        self.edit_service_btn.clicked.connect(self.edit_service_dialog)
        self.remove_service_btn.clicked.connect(self.remove_service)
        
        # Custom service connections
        self.add_custom_btn.clicked.connect(self.add_custom_service)
        self.test_custom_btn.clicked.connect(self.test_custom_service)
        
        # Services tools connections
        self.services_tools.service_checked.connect(self.update_service_status)
        self.services_tools.batch_complete.connect(self.update_summary)
        
        # Auto-refresh timer
        self.auto_refresh_timer.timeout.connect(self.refresh_all_services)
        
        # Tree selection
        self.service_tree.itemSelectionChanged.connect(self.on_service_selected)
        
    def load_default_services(self):
        """Load some default services for demonstration"""
        default_services = [
            {
                "name": "Google DNS",
                "url": "8.8.8.8",
                "type": "ping",
                "category": "Infrastructure"
            },
            {
                "name": "Cloudflare DNS",
                "url": "1.1.1.1", 
                "type": "ping",
                "category": "Infrastructure"
            }
        ]
        
        for service in default_services:
            self.services_tools.add_service(
                service["name"], service["url"], 
                service["type"], service["category"]
            )
        
        self.update_service_tree()
        
    def quick_add_service(self, name, url, category):
        """Quick add a service from category buttons"""
        self.info(f"Adding {name} to monitoring...")
        self.services_tools.add_service(name, url, "http", category)
        self.update_service_tree()
        self.success(f"✅ {name} added to service monitoring")
        
    def add_category_services(self, category_name, services):
        """Add all services from a category"""
        self.info(f"Adding all {category_name} services...")
        
        for service in services:
            self.services_tools.add_service(
                service["name"], service["url"], "http", category_name
            )
        
        self.update_service_tree()
        self.success(f"✅ Added all {category_name} services ({len(services)} total)")
        
    def add_custom_service(self):
        """Add custom service from the form"""
        name = self.service_name_edit.text().strip()
        url = self.service_url_edit.text().strip()
        check_type = self.check_type_combo.currentText().lower()
        category = self.category_combo.currentText()
        
        if not name or not url:
            self.error("Please enter both service name and URL")
            return
            
        # Convert check type to internal format
        type_mapping = {
            "http status (200 ok)": "http",
            "ping test": "ping",
            "port check": "port",
            "dns resolution": "dns",
            "custom api response": "api"
        }
        
        check_type_key = type_mapping.get(check_type, "http")
        
        self.info(f"Adding custom service: {name}")
        self.services_tools.add_service(name, url, check_type_key, category)
        
        # Clear form
        self.service_name_edit.clear()
        self.service_url_edit.clear()
        
        self.update_service_tree()
        self.success(f"✅ Custom service '{name}' added successfully")
        
    def test_custom_service(self):
        """Test the custom service configuration"""
        name = self.service_name_edit.text().strip() or "Test Service"
        url = self.service_url_edit.text().strip()
        check_type = self.check_type_combo.currentText().lower()
        
        if not url:
            self.error("Please enter a URL to test")
            return
            
        self.info(f"Testing service configuration: {url}")
        
        # Convert check type
        type_mapping = {
            "http status (200 ok)": "http",
            "ping test": "ping", 
            "port check": "port",
            "dns resolution": "dns",
            "custom api response": "api"
        }
        
        check_type_key = type_mapping.get(check_type, "http")
        self.services_tools.test_single_service(name, url, check_type_key)
        
    def update_service_tree(self):
        """Update the service tree display"""
        self.service_tree.clear()
        
        services_by_category = self.services_tools.get_services_by_category()
        
        for category, services in services_by_category.items():
            category_item = QTreeWidgetItem([f"📁 {category}", "", "", "", ""])
            category_item.setFont(0, QFont("Arial", 11, QFont.Bold))
            
            for service in services:
                service_item = QTreeWidgetItem([
                    service["name"],
                    "🔄 Checking...",
                    "N/A",
                    "Never",
                    service["url"]
                ])
                category_item.addChild(service_item)
            
            self.service_tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
        
        self.update_summary()
        
    def update_service_status(self, service_name, status, response_time, details):
        """Update individual service status in the tree"""
        # Find the service item in the tree
        root = self.service_tree.invisibleRootItem()
        
        for i in range(root.childCount()):
            category_item = root.child(i)
            
            for j in range(category_item.childCount()):
                service_item = category_item.child(j)
                
                if service_item.text(0) == service_name:
                    # Update status with icon
                    if status == "healthy":
                        status_text = "🟢 Online"
                        service_item.setBackground(1, QColor(212, 237, 218))
                    elif status == "warning":
                        status_text = "🟡 Warning"
                        service_item.setBackground(1, QColor(255, 243, 205))
                    else:
                        status_text = "🔴 Offline"
                        service_item.setBackground(1, QColor(248, 215, 218))
                    
                    service_item.setText(1, status_text)
                    service_item.setText(2, f"{response_time:.0f}ms" if response_time > 0 else "N/A")
                    service_item.setText(3, self.get_current_time())
                    
                    if details:
                        service_item.setToolTip(4, details)
                    
                    break
        
        self.update_summary()
        
    def get_current_time(self):
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def update_summary(self):
        """Update the status summary labels"""
        summary = self.services_tools.get_status_summary()
        
        self.total_services_label.setText(f"Total Services: {summary['total']}")
        self.healthy_services_label.setText(f"🟢 Healthy: {summary['healthy']}")
        self.warning_services_label.setText(f"🟡 Warning: {summary['warning']}")
        self.critical_services_label.setText(f"🔴 Critical: {summary['critical']}")
        
    def refresh_all_services(self):
        """Refresh all services"""
        self.info("🔄 Refreshing all service statuses...")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("🔄 Refreshing...")
        
        self.services_tools.check_all_services()
        
        # Re-enable button after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, self.restore_refresh_button)
        
    def restore_refresh_button(self):
        """Restore refresh button state"""
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh All")
        
    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh functionality"""
        if enabled:
            self.auto_refresh_timer.start(30000)  # 30 seconds
            self.info("🔄 Auto-refresh enabled (30 seconds)")
        else:
            self.auto_refresh_timer.stop()
            self.info("⏹️ Auto-refresh disabled")
            
    def add_service_dialog(self):
        """Show dialog to add a new service"""
        # This would open a more detailed dialog for service configuration
        self.info("💡 Use the Custom Service Management section below to add services")
        
    def edit_service_dialog(self):
        """Show dialog to edit selected service"""
        selected_items = self.service_tree.selectedItems()
        if not selected_items:
            self.warning("Please select a service to edit")
            return
            
        # For now, show info about the selected service
        item = selected_items[0]
        if item.parent():  # Make sure it's a service, not a category
            self.info(f"Selected service: {item.text(0)} - {item.text(4)}")
            self.info("💡 Full editing dialog would open here")
        else:
            self.warning("Please select a service (not a category)")
            
    def remove_service(self):
        """Remove selected service"""
        selected_items = self.service_tree.selectedItems()
        if not selected_items:
            self.warning("Please select a service to remove")
            return
            
        item = selected_items[0]
        if item.parent():  # Make sure it's a service, not a category
            service_name = item.text(0)
            
            reply = QMessageBox.question(
                self, 
                "Remove Service",
                f"Are you sure you want to remove '{service_name}' from monitoring?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.services_tools.remove_service(service_name)
                self.update_service_tree()
                self.success(f"✅ Service '{service_name}' removed from monitoring")
        else:
            self.warning("Please select a service (not a category)")
            
    def on_service_selected(self):
        """Handle service selection in tree"""
        selected_items = self.service_tree.selectedItems()
        if selected_items and selected_items[0].parent():
            service_name = selected_items[0].text(0)
            self.info(f"Selected service: {service_name}")
