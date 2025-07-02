# file_folder_permissions/permissions_tab.py
"""
AD Folder Permissions Tab - UI for analyzing folder permissions
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, 
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, 
    QProgressBar, QLabel, QGroupBox, QHeaderView, QCheckBox,
    QSplitter, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
from core.base_tab import BaseTab
from .permissions_tools import PermissionsTools, PermissionEntry


class PermissionsTableWidget(QTableWidget):
    """Custom table widget for displaying permissions"""
    
    def __init__(self):
        super().__init__()
        self.init_table()
    
    def init_table(self):
        """Initialize table structure"""
        headers = ['Path', 'Identity', 'Permission', 'Access Type', 'Inherited', 'Scan Time']
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table appearance and column resizing
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Path - user resizable
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Identity - user resizable  
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Permission - user resizable
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Access Type - auto size
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Inherited - auto size
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Scan Time - auto size
        
        # Set minimum column widths
        self.setColumnWidth(0, 250)  # Path
        self.setColumnWidth(1, 200)  # Identity
        self.setColumnWidth(2, 150)  # Permission
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSortingEnabled(True)
        
        # Enable word wrap for better text visibility
        self.setWordWrap(True)
        
        # Set default row height to accommodate wrapped text
        self.verticalHeader().setDefaultSectionSize(25)
    
    def populate_data(self, permissions: list, filter_text: str = ""):
        """Populate table with permission data"""
        # Filter data if needed
        if filter_text:
            filtered_permissions = [
                p for p in permissions 
                if filter_text.lower() in p.identity.lower() or 
                   filter_text.lower() in p.path.lower() or
                   filter_text.lower() in p.permission.lower()
            ]
        else:
            filtered_permissions = permissions
        
        self.setRowCount(len(filtered_permissions))
        
        for row, perm in enumerate(filtered_permissions):
            # Create items with proper text wrapping
            path_item = QTableWidgetItem(perm.path)
            path_item.setToolTip(perm.path)  # Show full path in tooltip
            
            identity_item = QTableWidgetItem(perm.identity)
            identity_item.setToolTip(perm.identity)
            
            permission_item = QTableWidgetItem(perm.permission)
            permission_item.setToolTip(perm.permission)
            
            access_item = QTableWidgetItem(perm.access_type)
            inherited_item = QTableWidgetItem("Yes" if perm.inherited else "No")
            time_item = QTableWidgetItem(perm.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            
            self.setItem(row, 0, path_item)
            self.setItem(row, 1, identity_item)
            self.setItem(row, 2, permission_item)
            self.setItem(row, 3, access_item)
            self.setItem(row, 4, inherited_item)
            self.setItem(row, 5, time_item)
        
        # Auto-resize rows to fit content
        self.resizeRowsToContents()


class PermissionsTab(BaseTab):
    """Main tab for folder permissions analysis"""
    
    def __init__(self, logger):
        super().__init__(logger)
        self.permissions_tools = PermissionsTools(logger)
        self.permissions_data = []
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create UI sections
        self.create_path_input_section(main_layout)
        self.create_filter_section(main_layout)
        self.create_results_section(main_layout)
        self.create_status_section(main_layout)
        
        # Apply styling
        self.apply_styling()
    
    def create_path_input_section(self, parent_layout):
        """Create the path input section"""
        path_group = QGroupBox("📁 Folder Selection")
        path_layout = QVBoxLayout(path_group)
        
        # Path input row
        input_row = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter UNC path (\\\\server\\share\\folder) or local folder path (C:\\folder)...")
        input_row.addWidget(QLabel("Path:"))
        input_row.addWidget(self.path_input)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setMinimumWidth(80)
        input_row.addWidget(self.browse_btn)
        
        path_layout.addLayout(input_row)
        
        # Options row
        options_row = QHBoxLayout()
        
        self.include_subfolders_cb = QCheckBox("Include subfolders")
        self.include_subfolders_cb.setChecked(True)
        self.include_subfolders_cb.setToolTip("Recursively scan all subdirectories")
        options_row.addWidget(self.include_subfolders_cb)
        
        self.scan_btn = QPushButton("🔍 Start Scan")
        self.scan_btn.setMinimumWidth(120)
        options_row.addWidget(self.scan_btn)
        
        options_row.addStretch()
        path_layout.addLayout(options_row)
        
        parent_layout.addWidget(path_group)
    
    def create_filter_section(self, parent_layout):
        """Create the filter section"""
        filter_group = QGroupBox("🔍 Filters & Search")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Search:"))
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by identity, path, or permission...")
        filter_layout.addWidget(self.filter_input)
        
        self.show_groups_only_cb = QCheckBox("Show AD Groups Only")
        self.show_groups_only_cb.setToolTip("Show only Active Directory groups, hide local users")
        filter_layout.addWidget(self.show_groups_only_cb)
        
        parent_layout.addWidget(filter_group)
    
    def create_results_section(self, parent_layout):
        """Create the results section"""
        results_group = QGroupBox("📊 Scan Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results toolbar
        toolbar_layout = QHBoxLayout()
        
        self.export_csv_btn = QPushButton("📄 Export All to CSV")
        self.export_csv_btn.setEnabled(False)
        toolbar_layout.addWidget(self.export_csv_btn)
        
        self.export_selected_csv_btn = QPushButton("📋 Export Selected to CSV")
        self.export_selected_csv_btn.setEnabled(False)
        toolbar_layout.addWidget(self.export_selected_csv_btn)
        
        self.export_json_btn = QPushButton("🔗 Export to JSON")
        self.export_json_btn.setEnabled(False)
        toolbar_layout.addWidget(self.export_json_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Results")
        self.clear_btn.setEnabled(False)
        toolbar_layout.addWidget(self.clear_btn)
        
        toolbar_layout.addStretch()
        
        # Statistics labels
        self.results_count_label = QLabel("0 entries")
        self.results_count_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        toolbar_layout.addWidget(self.results_count_label)
        
        results_layout.addLayout(toolbar_layout)
        
        # Results table
        self.results_table = PermissionsTableWidget()
        # Connect selection change to update export button state
        self.results_table.itemSelectionChanged.connect(self.update_export_buttons)
        results_layout.addWidget(self.results_table)
        
        # Summary section
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()
        results_layout.addLayout(summary_layout)
        
        parent_layout.addWidget(results_group)
    
    def create_status_section(self, parent_layout):
        """Create the status section"""
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready - Select a folder to analyze permissions")
        self.status_label.setStyleSheet("color: #333; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addLayout(status_layout)
    
    def setup_connections(self):
        """Initialize signal connections"""
        self.path_input.returnPressed.connect(self.start_scan)
        self.browse_btn.clicked.connect(self.browse_folder)
        self.scan_btn.clicked.connect(self.start_scan)
        self.filter_input.textChanged.connect(self.apply_filter)
        self.show_groups_only_cb.stateChanged.connect(self.apply_filter)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_selected_csv_btn.clicked.connect(self.export_selected_to_csv)
        self.export_json_btn.clicked.connect(self.export_to_json)
        self.clear_btn.clicked.connect(self.clear_results)
    
    def apply_styling(self):
        """Apply custom styling to the components"""
        button_style = """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
                border-color: #dee2e6;
            }
        """
        
        primary_button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 20px;
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
        
        # Apply styles
        self.scan_btn.setStyleSheet(primary_button_style)
        self.browse_btn.setStyleSheet(button_style)
        self.export_csv_btn.setStyleSheet(button_style)
        self.export_selected_csv_btn.setStyleSheet(button_style)
        self.export_json_btn.setStyleSheet(button_style)
        self.clear_btn.setStyleSheet(button_style)
        
        # Style input fields
        input_style = """
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
        """
        self.path_input.setStyleSheet(input_style)
        self.filter_input.setStyleSheet(input_style)
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Analyze", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            # Normalize the path for Windows
            import os
            normalized_folder = os.path.normpath(folder)
            self.path_input.setText(normalized_folder)
            self.info(f"Selected folder: {normalized_folder}")
    
    def start_scan(self):
        """Start the permission scanning process"""
        path = self.path_input.text().strip()
        
        if not path:
            QMessageBox.warning(self, "⚠️ Path Required", "Please enter a folder path or use Browse to select a folder.")
            return
        
        # Normalize the path to ensure Windows compatibility
        import os
        normalized_path = os.path.normpath(path)
        
        if not os.path.exists(normalized_path):
            QMessageBox.warning(self, "⚠️ Path Not Found", 
                              f"The specified path does not exist or is not accessible:\n{normalized_path}")
            return
        
        # Prepare UI for scanning
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanning...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Starting permission scan...")
        
        self.info(f"🔍 Starting permission scan for: {normalized_path}")
        if self.include_subfolders_cb.isChecked():
            self.info("📁 Including all subfolders in scan")
        
        # Start worker thread with normalized path
        self.permissions_tools.scan_folder_permissions_async(
            [normalized_path], 
            self.include_subfolders_cb.isChecked(),
            self.update_scan_progress,
            self.scan_completed,
            self.scan_error
        )
    
    def update_scan_progress(self, message: str):
        """Update scan progress"""
        self.status_label.setText(message)
        self.debug(f"Scan progress: {message}")
    
    def scan_completed(self, permissions: list):
        """Handle scan completion"""
        self.permissions_data = permissions
        self.apply_filter()  # This will populate the table
        
        # Update UI
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Start Scan")
        self.progress_bar.setVisible(False)
        self.export_csv_btn.setEnabled(len(permissions) > 0)
        self.export_selected_csv_btn.setEnabled(False)  # No selection yet
        self.export_json_btn.setEnabled(len(permissions) > 0)
        self.clear_btn.setEnabled(len(permissions) > 0)
        
        if len(permissions) > 0:
            self.status_label.setText(f"✅ Scan completed successfully!")
            self.success(f"📊 Found {len(permissions)} permission entries")
            
            # Update summary
            self.update_summary_stats()
            
            # Show helpful message about filtering
            if len(permissions) > 50:
                self.info("💡 Tip: Use the search filter or 'Show AD Groups Only' to narrow results")
        else:
            self.status_label.setText("⚠️ No permissions found")
            self.warning("No permissions found - check path accessibility and permissions")
            
            # Show more detailed message for troubleshooting
            path = self.path_input.text().strip()
            QMessageBox.information(self, "📋 No Permissions Found", 
                                  f"The path exists but no permissions were found.\n\n"
                                  f"This could happen if:\n"
                                  f"• You don't have sufficient privileges to read ACLs\n"
                                  f"• The path has no explicit permissions set\n"
                                  f"• There's an issue with the icacls command\n\n"
                                  f"💡 Try running SigmaToolkit as Administrator or check the path:\n{path}")
    
    def scan_error(self, error_message: str):
        """Handle scan error"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Start Scan")
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Scan failed")
        
        self.error(f"Scan error: {error_message}")
        QMessageBox.critical(self, "❌ Scan Error", 
                           f"An error occurred during scanning:\n\n{error_message}\n\n"
                           f"💡 Try:\n"
                           f"• Running as Administrator\n"
                           f"• Checking network connectivity for UNC paths\n"
                           f"• Verifying the path exists and is accessible")
    
    def apply_filter(self):
        """Apply current filters to the results table"""
        if not self.permissions_data:
            return
        
        # Get filtered data
        filtered_data = self.permissions_tools.filter_permissions(
            self.permissions_data,
            self.filter_input.text().strip(),
            self.show_groups_only_cb.isChecked()
        )
        
        # Populate table with filtered data
        self.results_table.populate_data(filtered_data, "")  # Empty filter since we already filtered
        
        # Update count
        display_count = len(filtered_data)
        total_count = len(self.permissions_data)
        
        if display_count != total_count:
            self.results_count_label.setText(f"📊 {display_count} of {total_count} entries")
        else:
            self.results_count_label.setText(f"📊 {total_count} entries")
        
        # Update summary for filtered data
        self.update_summary_stats(filtered_data)
    
    def update_summary_stats(self, permissions=None):
        """Update summary statistics display"""
        if permissions is None:
            permissions = self.permissions_data
        
        if not permissions:
            self.summary_label.setText("")
            return
        
        stats = self.permissions_tools.get_summary_stats(permissions)
        
        summary_text = (f"📁 {stats['unique_paths']} paths • "
                       f"👥 {stats['unique_identities']} identities • "
                       f"🏢 {stats['ad_groups']} AD groups • "
                       f"📋 {stats['inherited_permissions']} inherited • "
                       f"🔒 {stats['explicit_permissions']} explicit")
        
        if stats['deny_permissions'] > 0:
            summary_text += f" • ❌ {stats['deny_permissions']} deny permissions"
        
        self.summary_label.setText(summary_text)
    
    def update_export_buttons(self):
        """Update export button states based on selection"""
        selected_rows = len(self.results_table.selectionModel().selectedRows())
        self.export_selected_csv_btn.setEnabled(selected_rows > 0)
    
    def get_selected_permissions(self) -> list:
        """Get permission entries for currently selected rows"""
        selected_permissions = []
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        # Get currently displayed (filtered) data
        current_filter_text = self.filter_input.text().strip()
        show_ad_only = self.show_groups_only_cb.isChecked()
        filtered_data = self.permissions_tools.filter_permissions(
            self.permissions_data, current_filter_text, show_ad_only
        )
        
        for index in selected_rows:
            row = index.row()
            if row < len(filtered_data):
                selected_permissions.append(filtered_data[row])
        
        return selected_permissions
    
    def export_selected_to_csv(self):
        """Export selected results to CSV file"""
        selected_permissions = self.get_selected_permissions()
        
        if not selected_permissions:
            QMessageBox.information(self, "📋 No Selection", 
                                  "Please select one or more rows to export.\n\n"
                                  "💡 Click on row numbers to select rows.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Selected Permissions to CSV", 
            f"folder_permissions_selected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;All Files (*)"
        )
        
        if filename:
            success = self.permissions_tools.export_to_csv(selected_permissions, filename)
            if success:
                QMessageBox.information(self, "✅ Export Complete", 
                                      f"Successfully exported {len(selected_permissions)} selected entries to:\n{filename}")
    
    def export_to_csv(self):
        """Export all results to CSV file"""
        if not self.permissions_data:
            QMessageBox.information(self, "📋 No Data", "No permissions data to export. Please run a scan first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export All Permissions to CSV", 
            f"folder_permissions_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;All Files (*)"
        )
        
        if filename:
            success = self.permissions_tools.export_to_csv(self.permissions_data, filename)
            if success:
                QMessageBox.information(self, "✅ Export Complete", 
                                      f"Successfully exported {len(self.permissions_data)} entries to:\n{filename}")
    
    def export_to_json(self):
        """Export results to JSON file"""
        if not self.permissions_data:
            QMessageBox.information(self, "📋 No Data", "No permissions data to export. Please run a scan first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Permissions to JSON", 
            f"folder_permissions_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON files (*.json);;All Files (*)"
        )
        
        if filename:
            success = self.permissions_tools.export_to_json(self.permissions_data, filename)
            if success:
                QMessageBox.information(self, "✅ Export Complete", 
                                      f"Successfully exported {len(self.permissions_data)} entries to:\n{filename}")
    
    def clear_results(self):
        """Clear all results"""
        reply = QMessageBox.question(self, "🗑️ Clear Results", 
                                   "Are you sure you want to clear all scan results?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.permissions_data = []
            self.results_table.setRowCount(0)
            self.results_count_label.setText("📊 0 entries")
            self.summary_label.setText("")
            self.export_csv_btn.setEnabled(False)
            self.export_selected_csv_btn.setEnabled(False)
            self.export_json_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.status_label.setText("Ready - Results cleared")
            self.info("🗑️ Scan results cleared")