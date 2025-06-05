# mail/mail_tab.py - Updated with file upload functionality
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QGridLayout,
                            QTextEdit, QComboBox, QCheckBox, QSplitter,
                            QTreeWidget, QTreeWidgetItem, QTabWidget,
                            QScrollArea, QFrame, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.base_tab import BaseTab
from mail.mail_tools import MailTools

class MailTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.mail_tools = MailTools(logger)
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget for different analysis types
        self.analysis_tabs = QTabWidget()
        
        # Header Analysis Tab
        self.header_tab = self.create_header_analysis_tab()
        self.analysis_tabs.addTab(self.header_tab, "📧 Header Analysis")
        
        # SPF/DKIM/DMARC Tab
        self.auth_tab = self.create_authentication_tab()
        self.analysis_tabs.addTab(self.auth_tab, "🔐 Email Authentication")
        
        # Delivery Path Tab
        self.delivery_tab = self.create_delivery_path_tab()
        self.analysis_tabs.addTab(self.delivery_tab, "🛤️ Delivery Path")
        
        # Spam Analysis Tab
        self.spam_tab = self.create_spam_analysis_tab()
        self.analysis_tabs.addTab(self.spam_tab, "🛡️ Spam Analysis")
        
        layout.addWidget(self.analysis_tabs)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    def create_header_analysis_tab(self):
        """Create the main header analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header Input Section
        input_group = QGroupBox("Email Header Input")
        input_layout = QVBoxLayout(input_group)
        
        # Input method selection with file upload support
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Input Method:"))
        
        self.input_method_combo = QComboBox()
        self.input_method_combo.addItems([
            "Paste Headers Directly",
            "Upload .eml File",
            "Load from Gmail (if available)",
            "Load from Outlook (if available)"
        ])
        method_layout.addWidget(self.input_method_combo)
        
        # File upload button (initially hidden)
        self.upload_file_btn = QPushButton("📁 Browse & Upload .eml File")
        self.upload_file_btn.setVisible(False)  # Hidden by default
        method_layout.addWidget(self.upload_file_btn)
        
        method_layout.addStretch()
        input_layout.addLayout(method_layout)
        
        # File info label (for showing selected file)
        self.file_info_label = QLabel()
        self.file_info_label.setVisible(False)
        self.file_info_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4fd;
                border: 1px solid #0078d4;
                border-radius: 4px;
                padding: 8px;
                color: #0078d4;
                font-weight: bold;
            }
        """)
        input_layout.addWidget(self.file_info_label)
        
        # Header text input
        self.header_input = QTextEdit()
        self.header_input.setPlaceholderText(
            "Paste email headers here...\n\n"
            "Example headers to paste:\n"
            "Received: from mail.example.com...\n"
            "From: sender@example.com\n"
            "To: recipient@example.com\n"
            "Subject: Your Email Subject\n"
            "Date: Mon, 1 Jan 2024 12:00:00 +0000\n"
            "Message-ID: <123456@example.com>\n"
            "...\n\n"
            "Tip: Copy headers from 'View Source' or 'Show Original' in your email client\n"
            "Or select 'Upload .eml File' above to load from a saved email file"
        )
        self.header_input.setMinimumHeight(200)
        self.header_input.setFont(QFont("Consolas", 10))
        input_layout.addWidget(self.header_input)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.analyze_headers_btn = QPushButton("🔍 Analyze Headers")
        self.load_sample_btn = QPushButton("📋 Load Sample")
        self.clear_input_btn = QPushButton("🗑️ Clear Input")
        self.export_results_btn = QPushButton("💾 Export Results")
        
        button_layout.addWidget(self.analyze_headers_btn)
        button_layout.addWidget(self.load_sample_btn)
        button_layout.addWidget(self.clear_input_btn)
        button_layout.addWidget(self.export_results_btn)
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)
        
        # Analysis Results Section
        results_group = QGroupBox("Header Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        # Create splitter for organized results display
        results_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Header tree view
        self.header_tree = QTreeWidget()
        self.header_tree.setHeaderLabels(["Header Field", "Value"])
        self.header_tree.setMinimumWidth(400)
        results_splitter.addWidget(self.header_tree)
        
        # Right side: Analysis details
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Quick summary
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        analysis_layout.addWidget(QLabel("📊 Quick Summary:"))
        analysis_layout.addWidget(self.summary_text)
        
        # Detailed analysis
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setFont(QFont("Consolas", 9))
        analysis_layout.addWidget(QLabel("🔍 Detailed Analysis:"))
        analysis_layout.addWidget(self.analysis_text)
        
        results_splitter.addWidget(analysis_widget)
        results_splitter.setSizes([400, 600])
        
        results_layout.addWidget(results_splitter)
        layout.addWidget(results_group)
        
        # Style the buttons
        self.style_header_buttons()
        
        return widget
    
    def create_authentication_tab(self):
        """Create the email authentication analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Domain Input Section
        domain_group = QGroupBox("Email Authentication Analysis")
        domain_layout = QGridLayout(domain_group)
        
        domain_layout.addWidget(QLabel("Domain:"), 0, 0)
        self.auth_domain_edit = QLineEdit()
        self.auth_domain_edit.setPlaceholderText("example.com")
        domain_layout.addWidget(self.auth_domain_edit, 0, 1)
        
        domain_layout.addWidget(QLabel("Sender IP:"), 0, 2)
        self.sender_ip_edit = QLineEdit()
        self.sender_ip_edit.setPlaceholderText("192.168.1.100 (optional)")
        domain_layout.addWidget(self.sender_ip_edit, 0, 3)
        
        # Authentication test buttons
        auth_button_layout = QHBoxLayout()
        
        self.spf_check_btn = QPushButton("🛡️ Check SPF")
        self.dkim_check_btn = QPushButton("🔑 Check DKIM")
        self.dmarc_check_btn = QPushButton("📋 Check DMARC")
        self.comprehensive_auth_btn = QPushButton("🔒 Full Auth Analysis")
        
        auth_button_layout.addWidget(self.spf_check_btn)
        auth_button_layout.addWidget(self.dkim_check_btn)
        auth_button_layout.addWidget(self.dmarc_check_btn)
        auth_button_layout.addWidget(self.comprehensive_auth_btn)
        auth_button_layout.addStretch()
        
        domain_layout.addLayout(auth_button_layout, 1, 0, 1, 4)
        layout.addWidget(domain_group)
        
        # Authentication Results
        auth_results_group = QGroupBox("Authentication Analysis Results")
        auth_results_layout = QVBoxLayout(auth_results_group)
        
        self.auth_results_text = QTextEdit()
        self.auth_results_text.setReadOnly(True)
        self.auth_results_text.setFont(QFont("Consolas", 10))
        auth_results_layout.addWidget(self.auth_results_text)
        
        layout.addWidget(auth_results_group)
        
        # Authentication Guide
        guide_group = QGroupBox("Email Authentication Guide")
        guide_layout = QVBoxLayout(guide_group)
        
        guide_text = QTextEdit()
        guide_text.setMaximumHeight(120)
        guide_text.setReadOnly(True)
        guide_text.setText(
            "Email Authentication Overview:\n"
            "• SPF (Sender Policy Framework): Validates sending IP against DNS records\n"
            "• DKIM (DomainKeys Identified Mail): Cryptographic signature validation\n"
            "• DMARC (Domain Message Authentication): Policy for handling auth failures\n"
            "• Use 'Full Auth Analysis' for complete domain security assessment\n"
            "• Results help diagnose email delivery issues and spam problems"
        )
        guide_layout.addWidget(guide_text)
        
        layout.addWidget(guide_group)
        layout.addStretch()
        
        # Style authentication buttons
        self.style_auth_buttons()
        
        return widget
    
    def create_delivery_path_tab(self):
        """Create the delivery path analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Delivery Path Analysis
        path_group = QGroupBox("Email Delivery Path Analysis")
        path_layout = QVBoxLayout(path_group)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.show_timestamps_cb = QCheckBox("Show Timestamps")
        self.show_timestamps_cb.setChecked(True)
        
        self.show_delays_cb = QCheckBox("Calculate Delays")
        self.show_delays_cb.setChecked(True)
        
        self.show_servers_cb = QCheckBox("Analyze Servers")
        self.show_servers_cb.setChecked(True)
        
        self.reverse_order_cb = QCheckBox("Reverse Order (Newest First)")
        self.reverse_order_cb.setChecked(False)
        
        options_layout.addWidget(self.show_timestamps_cb)
        options_layout.addWidget(self.show_delays_cb)
        options_layout.addWidget(self.show_servers_cb)
        options_layout.addWidget(self.reverse_order_cb)
        options_layout.addStretch()
        
        path_layout.addLayout(options_layout)
        
        # Delivery path visualization
        self.delivery_path_text = QTextEdit()
        self.delivery_path_text.setReadOnly(True)
        self.delivery_path_text.setFont(QFont("Consolas", 10))
        path_layout.addWidget(self.delivery_path_text)
        
        layout.addWidget(path_group)
        
        # Delivery Statistics
        stats_group = QGroupBox("Delivery Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.delivery_stats_text = QTextEdit()
        self.delivery_stats_text.setMaximumHeight(100)
        self.delivery_stats_text.setReadOnly(True)
        stats_layout.addWidget(self.delivery_stats_text)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return widget
    
    def create_spam_analysis_tab(self):
        """Create the spam analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Spam Score Analysis
        spam_group = QGroupBox("Spam Score Analysis")
        spam_layout = QVBoxLayout(spam_group)
        
        # Spam check options
        check_layout = QHBoxLayout()
        
        self.check_blacklists_cb = QCheckBox("Check Blacklists")
        self.check_blacklists_cb.setChecked(True)
        
        self.check_reputation_cb = QCheckBox("Check IP Reputation")
        self.check_reputation_cb.setChecked(True)
        
        self.analyze_content_cb = QCheckBox("Analyze Content Patterns")
        self.analyze_content_cb.setChecked(True)
        
        check_layout.addWidget(self.check_blacklists_cb)
        check_layout.addWidget(self.check_reputation_cb)
        check_layout.addWidget(self.analyze_content_cb)
        check_layout.addStretch()
        
        spam_layout.addLayout(check_layout)
        
        # Spam analysis results
        self.spam_results_text = QTextEdit()
        self.spam_results_text.setReadOnly(True)
        self.spam_results_text.setFont(QFont("Consolas", 10))
        spam_layout.addWidget(self.spam_results_text)
        
        layout.addWidget(spam_group)
        
        # Reputation Check
        reputation_group = QGroupBox("IP Reputation Check")
        reputation_layout = QGridLayout(reputation_group)
        
        reputation_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.reputation_ip_edit = QLineEdit()
        self.reputation_ip_edit.setPlaceholderText("Enter IP from headers")
        reputation_layout.addWidget(self.reputation_ip_edit, 0, 1)
        
        self.check_reputation_btn = QPushButton("🔍 Check Reputation")
        reputation_layout.addWidget(self.check_reputation_btn, 0, 2)
        
        layout.addWidget(reputation_group)
        layout.addStretch()
        
        # Style spam analysis buttons
        self.style_spam_buttons()
        
        return widget
    
    def style_header_buttons(self):
        """Style the header analysis buttons"""
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
        
        utility_button_style = """
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
        
        upload_button_style = """
            QPushButton {
                background-color: #8764b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #7356a1;
            }
            QPushButton:pressed {
                background-color: #5f478a;
            }
        """
        
        self.analyze_headers_btn.setStyleSheet(main_button_style)
        self.load_sample_btn.setStyleSheet(utility_button_style)
        self.clear_input_btn.setStyleSheet(utility_button_style)
        self.export_results_btn.setStyleSheet(utility_button_style)
        self.upload_file_btn.setStyleSheet(upload_button_style)
    
    def style_auth_buttons(self):
        """Style the authentication buttons"""
        auth_button_style = """
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
        
        comprehensive_style = """
            QPushButton {
                background-color: #8764b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #7356a1;
            }
            QPushButton:pressed {
                background-color: #5f478a;
            }
        """
        
        self.spf_check_btn.setStyleSheet(auth_button_style)
        self.dkim_check_btn.setStyleSheet(auth_button_style)
        self.dmarc_check_btn.setStyleSheet(auth_button_style)
        self.comprehensive_auth_btn.setStyleSheet(comprehensive_style)
    
    def style_spam_buttons(self):
        """Style the spam analysis buttons"""
        spam_button_style = """
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
        
        self.check_reputation_btn.setStyleSheet(spam_button_style)
    
    def setup_connections(self):
        """Setup all signal connections"""
        # Header analysis connections
        self.analyze_headers_btn.clicked.connect(self.analyze_email_headers)
        self.load_sample_btn.clicked.connect(self.load_sample_headers)
        self.clear_input_btn.clicked.connect(self.clear_input)
        self.export_results_btn.clicked.connect(self.export_results)
        self.upload_file_btn.clicked.connect(self.upload_eml_file)
        
        # Input method change connection
        self.input_method_combo.currentTextChanged.connect(self.on_input_method_changed)
        
        # Authentication connections
        self.spf_check_btn.clicked.connect(self.check_spf)
        self.dkim_check_btn.clicked.connect(self.check_dkim)
        self.dmarc_check_btn.clicked.connect(self.check_dmarc)
        self.comprehensive_auth_btn.clicked.connect(self.comprehensive_auth_check)
        self.check_reputation_btn.clicked.connect(self.check_ip_reputation)
        
        # Mail tools connections
        self.mail_tools.result_ready.connect(self.handle_result)
        self.mail_tools.analysis_ready.connect(self.handle_analysis)
        
        # Delivery path options
        self.show_timestamps_cb.toggled.connect(self.update_delivery_path)
        self.show_delays_cb.toggled.connect(self.update_delivery_path)
        self.show_servers_cb.toggled.connect(self.update_delivery_path)
        self.reverse_order_cb.toggled.connect(self.update_delivery_path)
        
        # Auto-extract domain from headers
        self.header_input.textChanged.connect(self.auto_extract_domain)
    
    def on_input_method_changed(self, method):
        """Handle input method selection change"""
        if method == "Upload .eml File":
            self.upload_file_btn.setVisible(True)
            self.header_input.setPlaceholderText(
                "Click 'Browse & Upload .eml File' button above to load email from file...\n\n"
                "Supported formats:\n"
                "• .eml files (standard email format)\n"
                "• .msg files (Outlook format - experimental)\n"
                "• .txt files containing email headers\n\n"
                "Or manually paste headers below if you prefer."
            )
        else:
            self.upload_file_btn.setVisible(False)
            self.file_info_label.setVisible(False)
            if method == "Paste Headers Directly":
                self.header_input.setPlaceholderText(
                    "Paste email headers here...\n\n"
                    "Example headers to paste:\n"
                    "Received: from mail.example.com...\n"
                    "From: sender@example.com\n"
                    "To: recipient@example.com\n"
                    "Subject: Your Email Subject\n"
                    "Date: Mon, 1 Jan 2024 12:00:00 +0000\n"
                    "Message-ID: <123456@example.com>\n"
                    "...\n\n"
                    "Tip: Copy headers from 'View Source' or 'Show Original' in your email client"
                )
            elif method.startswith("Load from"):
                self.header_input.setPlaceholderText(
                    f"{method} - Feature coming soon!\n\n"
                    "This will allow direct integration with email clients.\n"
                    "For now, please use 'Paste Headers Directly' or 'Upload .eml File'."
                )
    
    def upload_eml_file(self):
        """Handle .eml file upload"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Email File",
                "",
                "Email Files (*.eml *.msg *.txt);;All Files (*)"
            )
            
            if file_path:
                self.info(f"Loading email file: {file_path}")
                
                # Read the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except UnicodeDecodeError:
                    # Try with different encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            file_content = f.read()
                    except Exception as e:
                        self.error(f"Could not read file with any encoding: {str(e)}")
                        return
                
                # Check if it's a valid email format
                if not self.validate_email_content(file_content):
                    reply = QMessageBox.question(
                        self, 
                        "Invalid Email Format", 
                        "The selected file doesn't appear to contain valid email headers.\n\n"
                        "Do you want to load it anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                
                # Load content into text area
                self.header_input.setPlainText(file_content)
                
                # Show file info
                import os
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                self.file_info_label.setText(
                    f"📁 Loaded: {file_name} ({file_size:,} bytes)"
                )
                self.file_info_label.setVisible(True)
                
                self.success(f"Successfully loaded email file: {file_name}")
                
                # Auto-extract domain information
                self.auto_extract_domain()
                
        except Exception as e:
            self.error(f"Failed to upload file: {str(e)}")
    
    def validate_email_content(self, content):
        """Validate if content contains email headers"""
        # Check for common email headers
        email_headers = [
            'from:', 'to:', 'subject:', 'date:', 'message-id:', 
            'received:', 'return-path:', 'mime-version:'
        ]
        
        content_lower = content.lower()
        found_headers = sum(1 for header in email_headers if header in content_lower)
        
        # Consider valid if at least 3 common headers are found
        return found_headers >= 3
    
    def handle_result(self, message, level):
        """Handle results from mail tools"""
        if level == "SUCCESS":
            self.success(message)
        elif level == "ERROR":
            self.error(message)
        elif level == "WARNING":
            self.warning(message)
        else:
            self.info(message)
    
    def handle_analysis(self, analysis_data, analysis_type):
        """Handle analysis results from mail tools"""
        if analysis_type == "headers":
            self.display_header_analysis(analysis_data)
        elif analysis_type == "authentication":
            self.display_auth_analysis(analysis_data)
        elif analysis_type == "delivery_path":
            self.display_delivery_path(analysis_data)
        elif analysis_type == "spam":
            self.display_spam_analysis(analysis_data)
    
    def analyze_email_headers(self):
        """Analyze email headers"""
        headers_text = self.header_input.toPlainText().strip()
        if not headers_text:
            self.error("Please paste email headers to analyze or upload an .eml file")
            return
        
        self.analyze_headers_btn.setEnabled(False)
        self.info("Analyzing email headers...")
        
        # Clear previous results
        self.header_tree.clear()
        self.summary_text.clear()
        self.analysis_text.clear()
        
        self.mail_tools.analyze_headers(headers_text)
        
        # Re-enable button after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.analyze_headers_btn.setEnabled(True))
    
    def load_sample_headers(self):
        """Load sample email headers for testing"""
        sample_headers = """Delivered-To: user@example.com
Received: by 2002:a17:90b:1234:b0:1a2:3b4c:5d6e with SMTP id abc123-v1.1.1.1
        for <user@example.com>; Mon, 27 May 2024 10:30:15 -0700 (PDT)
Received: from mail.sender.com (mail.sender.com. [203.0.113.10])
        by mx.google.com with ESMTPS id xyz789-v6.0.1.1
        (version=TLS1_3 cipher=TLS_AES_256_GCM_SHA384 bits=256/256);
        Mon, 27 May 2024 10:30:14 -0700 (PDT)
Received: from internal.sender.com (internal.sender.com [192.168.1.50])
        by mail.sender.com with ESMTP id qwerty123;
        Mon, 27 May 2024 17:30:13 +0000
Message-ID: <20240527173013.ABC123@sender.com>
Date: Mon, 27 May 2024 17:30:13 +0000
From: "John Doe" <john.doe@sender.com>
To: user@example.com
Subject: Test Email for Header Analysis
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Authentication-Results: mx.google.com;
       spf=pass (google.com: domain of john.doe@sender.com designates 203.0.113.10 as permitted sender) smtp.mailfrom=john.doe@sender.com;
       dkim=pass (test mode) header.i=@sender.com;
       dmarc=pass (p=QUARANTINE sp=QUARANTINE dis=NONE) header.from=sender.com
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=sender.com; s=default;
        h=from:to:subject:date:message-id; bh=abc123def456==; b=xyz789abc123==
SPF: PASS
Return-Path: <john.doe@sender.com>

This is a sample email for testing header analysis functionality."""

        self.header_input.setPlainText(sample_headers)
        self.file_info_label.setVisible(False)  # Hide file info when loading sample
        self.info("Sample email headers loaded")
    
    def clear_input(self):
        """Clear all input fields"""
        self.header_input.clear()
        self.header_tree.clear()
        self.summary_text.clear()
        self.analysis_text.clear()
        self.auth_results_text.clear()
        self.delivery_path_text.clear()
        self.delivery_stats_text.clear()
        self.spam_results_text.clear()
        self.file_info_label.setVisible(False)
        self.info("Input and results cleared")
    
    def export_results(self):
        """Export analysis results"""
        try:
            # Get all results
            headers = self.header_input.toPlainText()
            summary = self.summary_text.toPlainText()
            analysis = self.analysis_text.toPlainText()
            auth_results = self.auth_results_text.toPlainText()
            
            if not any([headers, summary, analysis, auth_results]):
                self.warning("No analysis results to export")
                return
            
            # Choose file location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Analysis Results", 
                "mail_analysis_results.txt", 
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("SigmaToolkit Mail Header Analysis Results\n")
                    f.write("=" * 50 + "\n\n")
                    
                    if headers:
                        f.write("ORIGINAL HEADERS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(headers + "\n\n")
                    
                    if summary:
                        f.write("SUMMARY:\n")
                        f.write("-" * 20 + "\n")
                        f.write(summary + "\n\n")
                    
                    if analysis:
                        f.write("DETAILED ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(analysis + "\n\n")
                    
                    if auth_results:
                        f.write("AUTHENTICATION RESULTS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(auth_results + "\n\n")
                
                self.success(f"Results exported to: {file_path}")
                
        except Exception as e:
            self.error(f"Export failed: {str(e)}")
    
    def auto_extract_domain(self):
        """Auto-extract domain from headers for authentication checks"""
        headers_text = self.header_input.toPlainText()
        
        # Try to extract domain from From field
        import re
        from_match = re.search(r'From:.*?@([a-zA-Z0-9.-]+)', headers_text, re.IGNORECASE)
        if from_match and not self.auth_domain_edit.text():
            domain = from_match.group(1)
            self.auth_domain_edit.setText(domain)
        
        # Try to extract sender IP from Received headers
        ip_match = re.search(r'Received:.*?\[(\d+\.\d+\.\d+\.\d+)\]', headers_text)
        if ip_match and not self.sender_ip_edit.text():
            ip = ip_match.group(1)
            self.sender_ip_edit.setText(ip)
            self.reputation_ip_edit.setText(ip)
    
    def check_spf(self):
        """Check SPF records for domain"""
        domain = self.auth_domain_edit.text().strip()
        sender_ip = self.sender_ip_edit.text().strip()
        
        if not domain:
            self.error("Please enter a domain to check SPF")
            return
        
        self.spf_check_btn.setEnabled(False)
        self.info(f"Checking SPF records for {domain}...")
        
        self.mail_tools.check_spf(domain, sender_ip)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.spf_check_btn.setEnabled(True))
    
    def check_dkim(self):
        """Check DKIM records for domain"""
        domain = self.auth_domain_edit.text().strip()
        
        if not domain:
            self.error("Please enter a domain to check DKIM")
            return
        
        self.dkim_check_btn.setEnabled(False)
        self.info(f"Checking DKIM records for {domain}...")
        
        self.mail_tools.check_dkim(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.dkim_check_btn.setEnabled(True))
    
    def check_dmarc(self):
        """Check DMARC records for domain"""
        domain = self.auth_domain_edit.text().strip()
        
        if not domain:
            self.error("Please enter a domain to check DMARC")
            return
        
        self.dmarc_check_btn.setEnabled(False)
        self.info(f"Checking DMARC records for {domain}...")
        
        self.mail_tools.check_dmarc(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.dmarc_check_btn.setEnabled(True))
    
    def comprehensive_auth_check(self):
        """Run comprehensive authentication check"""
        domain = self.auth_domain_edit.text().strip()
        sender_ip = self.sender_ip_edit.text().strip()
        
        if not domain:
            self.error("Please enter a domain for comprehensive check")
            return
        
        self.comprehensive_auth_btn.setEnabled(False)
        self.info(f"Running comprehensive authentication analysis for {domain}...")
        
        self.mail_tools.comprehensive_auth_check(domain, sender_ip)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(15000, lambda: self.comprehensive_auth_btn.setEnabled(True))
    
    def check_ip_reputation(self):
        """Check IP reputation"""
        ip = self.reputation_ip_edit.text().strip()
        
        if not ip:
            self.error("Please enter an IP address to check")
            return
        
        self.check_reputation_btn.setEnabled(False)
        self.info(f"Checking reputation for IP {ip}...")
        
        self.mail_tools.check_ip_reputation(ip)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10000, lambda: self.check_reputation_btn.setEnabled(True))
    
    def display_header_analysis(self, analysis_data):
        """Display header analysis results"""
        # Populate header tree
        self.header_tree.clear()
        if 'headers' in analysis_data:
            for header, value in analysis_data['headers'].items():
                item = QTreeWidgetItem([header, value])
                self.header_tree.addTopLevelItem(item)
        
        # Update summary
        if 'summary' in analysis_data:
            self.summary_text.setPlainText(analysis_data['summary'])
        
        # Update detailed analysis
        if 'analysis' in analysis_data:
            self.analysis_text.setPlainText(analysis_data['analysis'])
        
        # Update delivery path if available
        if 'delivery_path' in analysis_data:
            self.display_delivery_path(analysis_data['delivery_path'])
    
    def display_auth_analysis(self, analysis_data):
        """Display authentication analysis results"""
        self.auth_results_text.setPlainText(analysis_data.get('results', ''))
    
    def display_delivery_path(self, path_data):
        """Display delivery path analysis"""
        if isinstance(path_data, dict):
            self.delivery_path_text.setPlainText(path_data.get('path', ''))
            self.delivery_stats_text.setPlainText(path_data.get('stats', ''))
        else:
            self.delivery_path_text.setPlainText(str(path_data))
    
    def display_spam_analysis(self, spam_data):
        """Display spam analysis results"""
        self.spam_results_text.setPlainText(spam_data.get('results', ''))
    
    def update_delivery_path(self):
        """Update delivery path display based on options"""
        # This would re-analyze the delivery path with current options
        if hasattr(self, '_last_analysis_data') and self._last_analysis_data:
            headers_text = self.header_input.toPlainText()
            if headers_text:
                options = {
                    'show_timestamps': self.show_timestamps_cb.isChecked(),
                    'show_delays': self.show_delays_cb.isChecked(),
                    'show_servers': self.show_servers_cb.isChecked(),
                    'reverse_order': self.reverse_order_cb.isChecked()
                }
                self.mail_tools.analyze_delivery_path(headers_text, options)