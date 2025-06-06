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
        self.config_file_path = "service_config.json"  # Default config file
        self.init_ui()
        self.setup_connections()
        self.load_default_services()
        self.auto_load_config()  # Auto-load saved configuration
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Service Status Overview Section
        overview_group = QGroupBox("🟢 Service Status Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh All")
        self.test_selected_btn = QPushButton("🧪 Test Selected")
        self.auto_refresh_cb = QCheckBox("Auto-refresh (30s)")
        self.save_config_btn = QPushButton("💾 Save Config")
        self.load_config_btn = QPushButton("📁 Load Config")
        self.add_service_btn = QPushButton("➕ Add Service")
        self.edit_service_btn = QPushButton("✏️ Edit Service")
        self.remove_service_btn = QPushButton("🗑️ Remove Service")
        
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.test_selected_btn)
        control_layout.addWidget(self.auto_refresh_cb)
        control_layout.addWidget(self.save_config_btn)
        control_layout.addWidget(self.load_config_btn)
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
        
        # Enable context menu for individual service actions
        self.service_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.service_tree.customContextMenuRequested.connect(self.show_service_context_menu)
        
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
        
        # Infrastructure Category
        infra_frame = self.create_category_frame("Infrastructure", [
            {"name": "Google DNS", "url": "8.8.8.8"},
            {"name": "Cloudflare DNS", "url": "1.1.1.1"},
            {"name": "Quad9 DNS", "url": "9.9.9.9"},
            {"name": "OpenDNS", "url": "208.67.222.222"}
        ])
        
        # Cloud Providers Category
        cloud_frame = self.create_category_frame("Cloud Providers", [
            {"name": "AWS Console", "url": "https://console.aws.amazon.com"},
            {"name": "Azure Portal", "url": "https://portal.azure.com"},
            {"name": "Google Cloud", "url": "https://console.cloud.google.com"},
            {"name": "Cloudflare", "url": "https://dash.cloudflare.com"}
        ])
        
        categories_layout.addWidget(ms365_frame)
        categories_layout.addWidget(infra_frame)
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
            "• Right-click services for individual testing and management\n"
            "• Use 🧪 Test Selected button to test only the selected service\n"
            "• Services are automatically saved when added or removed • Enable auto-refresh for continuous monitoring"
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
            
        # Test selected button style (special orange color)
        self.test_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff8c00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #e67300;
            }
            QPushButton:pressed {
                background-color: #cc6600;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
            
        for btn in [self.save_config_btn, self.load_config_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #8764b8;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7356a1;
                }
                QPushButton:pressed {
                    background-color: #5f478a;
                }
            """)
            
        for btn in [self.add_service_btn, self.edit_service_btn, self.remove_service_btn]:
            btn.setStyleSheet(management_button_style)
        
    def setup_connections(self):
        # Main control connections
        self.refresh_btn.clicked.connect(self.refresh_all_services)
        self.test_selected_btn.clicked.connect(self.test_selected_service)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        self.save_config_btn.clicked.connect(self.save_service_config)
        self.load_config_btn.clicked.connect(self.load_service_config)
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
        self.auto_save_config()  # Auto-save after adding
        self.success(f"✅ {name} added to service monitoring")
        
    def add_category_services(self, category_name, services):
        """Add all services from a category"""
        self.info(f"Adding all {category_name} services...")
        
        for service in services:
            self.services_tools.add_service(
                service["name"], service["url"], "http", category_name
            )
        
        self.update_service_tree()
        self.auto_save_config()  # Auto-save after adding multiple services
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
        self.auto_save_config()  # Auto-save after adding custom service
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
                self.auto_save_config()  # Auto-save after removing
                self.success(f"✅ Service '{service_name}' removed from monitoring")
        else:
            self.warning("Please select a service (not a category)")
            
    def on_service_selected(self):
        """Handle service selection in tree"""
        selected_items = self.service_tree.selectedItems()
        has_service_selected = selected_items and selected_items[0].parent() is not None
        
        # Enable/disable Test Selected button based on selection
        self.test_selected_btn.setEnabled(has_service_selected)
        
        if has_service_selected:
            service_name = selected_items[0].text(0)
            self.info(f"Selected service: {service_name}")
            
    def test_selected_service(self):
        """Test only the selected service"""
        selected_items = self.service_tree.selectedItems()
        if not selected_items:
            self.warning("Please select a service to test")
            return
            
        item = selected_items[0]
        if not item.parent():  # Make sure it's a service, not a category
            self.warning("Please select a service (not a category)")
            return
            
        service_name = item.text(0)
        self.info(f"🧪 Testing selected service: {service_name}")
        
        # Find the service in our services dictionary
        service_to_test = None
        for service_id, service in self.services_tools.services.items():
            if service["name"] == service_name:
                service_to_test = service
                break
                
        if service_to_test:
            self.test_selected_btn.setEnabled(False)
            self.test_selected_btn.setText("🧪 Testing...")
            
            # Update the service status to show it's being tested
            item.setText(1, "🔄 Testing...")
            item.setBackground(1, QColor(255, 255, 224))  # Light yellow background
            
            # Test the single service
            def _test_single():
                self.services_tools._check_single_service(service_to_test)
                
            import threading
            thread = threading.Thread(target=_test_single)
            thread.daemon = True
            thread.start()
            
            # Re-enable button after delay
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(5000, self.restore_test_selected_button)
        else:
            self.error(f"Could not find service configuration for: {service_name}")
            
    def restore_test_selected_button(self):
        """Restore test selected button state"""
        self.test_selected_btn.setEnabled(True)
        self.test_selected_btn.setText("🧪 Test Selected")
        
    def show_service_context_menu(self, position):
        """Show context menu for service tree items"""
        item = self.service_tree.itemAt(position)
        if not item:
            return
            
        from PyQt5.QtWidgets import QMenu, QAction
        menu = QMenu()
        
        if item.parent():  # It's a service item
            service_name = item.text(0)
            
            # Test service action
            test_action = QAction("🧪 Test This Service", self)
            test_action.triggered.connect(lambda: self.test_single_service_by_name(service_name))
            menu.addAction(test_action)
            
            menu.addSeparator()
            
            # Copy service info action
            copy_action = QAction("📋 Copy Service Info", self)
            copy_action.triggered.connect(lambda: self.copy_service_info(service_name))
            menu.addAction(copy_action)
            
            # Edit service action
            edit_action = QAction("✏️ Edit Service", self)
            edit_action.triggered.connect(lambda: self.edit_specific_service(service_name))
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
            # Remove service action
            remove_action = QAction("🗑️ Remove Service", self)
            remove_action.triggered.connect(lambda: self.remove_specific_service(service_name))
            menu.addAction(remove_action)
            
        else:  # It's a category item
            category_name = item.text(0).replace("📁 ", "")
            
            # Test all services in category
            test_category_action = QAction(f"🧪 Test All {category_name}", self)
            test_category_action.triggered.connect(lambda: self.test_category_services(category_name))
            menu.addAction(test_category_action)
            
            # Expand/collapse category
            if item.isExpanded():
                collapse_action = QAction("📁 Collapse Category", self)
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
                menu.addAction(collapse_action)
            else:
                expand_action = QAction("📂 Expand Category", self)
                expand_action.triggered.connect(lambda: item.setExpanded(True))
                menu.addAction(expand_action)
        
        # Show the context menu
        menu.exec_(self.service_tree.mapToGlobal(position))
        
    def test_single_service_by_name(self, service_name):
        """Test a single service by name (used by context menu)"""
        # Find and select the service in the tree first
        root = self.service_tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            for j in range(category_item.childCount()):
                service_item = category_item.child(j)
                if service_item.text(0) == service_name:
                    self.service_tree.setCurrentItem(service_item)
                    self.test_selected_service()
                    return
        
        self.error(f"Could not find service: {service_name}")
        
    def copy_service_info(self, service_name):
        """Copy service information to clipboard"""
        # Find the service configuration
        service_config = None
        for service_id, service in self.services_tools.services.items():
            if service["name"] == service_name:
                service_config = service
                break
                
        if service_config:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            
            # Get the latest status
            service_key = f"{service_config['category']}_{service_name}".replace(" ", "_")
            result = self.services_tools.last_check_results.get(service_key, {})
            
            service_info = f"""Service: {service_name}
URL: {service_config['url']}
Type: {service_config['type']}
Category: {service_config['category']}
Status: {result.get('status', 'Unknown')}
Response Time: {result.get('response_time', 0):.0f}ms
Last Checked: {result.get('last_checked', 'Never')}
Details: {result.get('details', 'N/A')}"""
            
            clipboard.setText(service_info)
            self.success(f"📋 Service info copied for: {service_name}")
        else:
            self.error(f"Could not find service configuration for: {service_name}")
            
    def edit_specific_service(self, service_name):
        """Edit a specific service (placeholder for future implementation)"""
        self.info(f"✏️ Edit service: {service_name}")
        self.info("💡 Full editing dialog will be implemented in future version")
        
    def remove_specific_service(self, service_name):
        """Remove a specific service"""
        from PyQt5.QtWidgets import QMessageBox
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
            self.auto_save_config()
            self.success(f"✅ Service '{service_name}' removed from monitoring")
            
    def test_category_services(self, category_name):
        """Test all services in a specific category"""
        self.info(f"🧪 Testing all services in category: {category_name}")
        
        # Find all services in the category
        services_to_test = []
        for service_id, service in self.services_tools.services.items():
            if service["category"] == category_name and service["enabled"]:
                services_to_test.append(service)
        
        if not services_to_test:
            self.warning(f"No enabled services found in category: {category_name}")
            return
            
        self.info(f"Testing {len(services_to_test)} services in {category_name}...")
        
        # Test each service in the category
        def _test_category():
            for service in services_to_test:
                self.services_tools._check_single_service(service)
                import time
                time.sleep(0.5)  # Small delay between tests
                
        import threading
        thread = threading.Thread(target=_test_category)
        thread.daemon = True
        thread.start()
            
    def auto_save_config(self):
        """Automatically save the current configuration"""
        try:
            success = self.services_tools.save_services_to_config(self.config_file_path)
            if success:
                self.debug(f"Configuration auto-saved to {self.config_file_path}")
            else:
                self.debug("Auto-save failed")
        except Exception as e:
            self.debug(f"Auto-save error: {str(e)}")
            
    def auto_load_config(self):
        """Automatically load configuration if it exists"""
        try:
            import os
            if os.path.exists(self.config_file_path):
                success = self.services_tools.load_services_from_config(self.config_file_path)
                if success:
                    self.update_service_tree()
                    self.info(f"📁 Loaded previous configuration ({len(self.services_tools.services)} services)")
                else:
                    self.debug("Auto-load failed")
            else:
                self.debug("No previous configuration found")
        except Exception as e:
            self.debug(f"Auto-load error: {str(e)}")
            
    def save_service_config(self):
        """Save service configuration to file with dialog"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Service Configuration",
                f"service_config_{self.get_current_time().replace(':', '-')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                success = self.services_tools.save_services_to_config(file_path)
                if success:
                    self.success(f"💾 Configuration saved to: {file_path}")
                    # Also update the default config file
                    self.services_tools.save_services_to_config(self.config_file_path)
                else:
                    self.error("Failed to save configuration")
                    
        except Exception as e:
            self.error(f"Save configuration failed: {str(e)}")
            
    def load_service_config(self):
        """Load service configuration from file with dialog"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Service Configuration",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Ask if user wants to replace current services or add to them
                reply = QMessageBox.question(
                    self,
                    "Load Configuration",
                    "Do you want to replace current services with the loaded configuration?\n\n"
                    "Choose 'Yes' to replace all services\n"
                    "Choose 'No' to add to existing services",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Cancel:
                    return
                    
                if reply == QMessageBox.Yes:
                    # Clear existing services
                    self.services_tools.services.clear()
                    self.services_tools.last_check_results.clear()
                    
                success = self.services_tools.load_services_from_config(file_path)
                if success:
                    self.update_service_tree()
                    self.auto_save_config()  # Save to default config
                    action = "replaced" if reply == QMessageBox.Yes else "added to"
                    self.success(f"📁 Configuration loaded and {action} current services")
                else:
                    self.error("Failed to load configuration")
                    
        except Exception as e:
            self.error(f"Load configuration failed: {str(e)}")
