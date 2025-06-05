# dns/dns_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QGridLayout,
                            QFrame, QComboBox, QTextEdit)
from PyQt5.QtCore import Qt
from core.base_tab import BaseTab
from dns.dns_tools import DNSTools

class DNSTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.dns_tools = DNSTools(logger)
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Quick DNS Lookups Section
        quick_group = QGroupBox("Quick DNS Lookups")
        quick_layout = QGridLayout(quick_group)
        
        quick_layout.addWidget(QLabel("Domain/IP:"), 0, 0)
        self.quick_domain_edit = QLineEdit()
        self.quick_domain_edit.setPlaceholderText("Enter domain name or IP address")
        quick_layout.addWidget(self.quick_domain_edit, 0, 1, 1, 2)
        
        # Quick action buttons
        self.forward_btn = QPushButton("Forward Lookup")
        self.reverse_btn = QPushButton("Reverse Lookup")
        self.all_records_btn = QPushButton("All Records")
        
        quick_layout.addWidget(self.forward_btn, 1, 0)
        quick_layout.addWidget(self.reverse_btn, 1, 1)
        quick_layout.addWidget(self.all_records_btn, 1, 2)
        
        layout.addWidget(quick_group)
        
        # Specific Record Types Section
        records_group = QGroupBox("Specific DNS Record Lookups")
        records_layout = QGridLayout(records_group)
        
        records_layout.addWidget(QLabel("Domain:"), 0, 0)
        self.records_domain_edit = QLineEdit()
        self.records_domain_edit.setPlaceholderText("Enter domain name")
        records_layout.addWidget(self.records_domain_edit, 0, 1, 1, 3)
        
        # Record type buttons - now including A record
        self.a_btn = QPushButton("A Records\n(IPv4)")
        self.mx_btn = QPushButton("MX Records\n(Mail)")
        self.txt_btn = QPushButton("TXT Records\n(SPF/DKIM)")
        self.ns_btn = QPushButton("NS Records\n(Name Servers)")
        self.cname_btn = QPushButton("CNAME Records\n(Aliases)")
        self.aaaa_btn = QPushButton("AAAA Records\n(IPv6)")
        
        # Arrange buttons in a 3x2 grid
        records_layout.addWidget(self.a_btn, 1, 0)
        records_layout.addWidget(self.mx_btn, 1, 1)
        records_layout.addWidget(self.txt_btn, 1, 2)
        records_layout.addWidget(self.ns_btn, 2, 0)
        records_layout.addWidget(self.cname_btn, 2, 1)
        records_layout.addWidget(self.aaaa_btn, 2, 2)
        
        layout.addWidget(records_group)
        
        # DNS Server Selection Section
        server_group = QGroupBox("DNS Server Selection")
        server_layout = QHBoxLayout(server_group)
        
        server_layout.addWidget(QLabel("DNS Server:"))
        self.dns_server_combo = QComboBox()
        self.dns_server_combo.addItems([
            "System Default",
            "Google DNS (8.8.8.8)",
            "Cloudflare DNS (1.1.1.1)",
            "Quad9 DNS (9.9.9.9)",
            "OpenDNS (208.67.222.222)",
            "Custom..."
        ])
        server_layout.addWidget(self.dns_server_combo)
        
        self.custom_dns_edit = QLineEdit()
        self.custom_dns_edit.setPlaceholderText("Enter custom DNS server IP")
        self.custom_dns_edit.setEnabled(False)
        server_layout.addWidget(self.custom_dns_edit)
        
        server_layout.addStretch()
        
        layout.addWidget(server_group)
        
        # Common Domains Section
        common_group = QGroupBox("Quick Test Domains")
        common_layout = QHBoxLayout(common_group)
        
        self.test_google_btn = QPushButton("Test google.com")
        self.test_ms_btn = QPushButton("Test microsoft.com")
        self.test_github_btn = QPushButton("Test github.com")
        self.test_local_btn = QPushButton("Test Local Domain")
        
        common_layout.addWidget(self.test_google_btn)
        common_layout.addWidget(self.test_ms_btn)
        common_layout.addWidget(self.test_github_btn)
        common_layout.addWidget(self.test_local_btn)
        common_layout.addStretch()
        
        layout.addWidget(common_group)
        
        # DNS Troubleshooting Section
        trouble_group = QGroupBox("DNS Troubleshooting")
        trouble_layout = QVBoxLayout(trouble_group)
        
        trouble_info = QTextEdit()
        trouble_info.setMaximumHeight(80)
        trouble_info.setReadOnly(True)
        trouble_info.setText(
            "DNS Troubleshooting Tips:\n"
            "• Use 'All Records' for comprehensive domain analysis\n"
            "• Check A records for basic IPv4 resolution\n"
            "• Check MX records for email delivery issues\n"
            "• Verify SPF records in TXT lookup for email authentication\n"
            "• Compare results with different DNS servers"
        )
        trouble_layout.addWidget(trouble_info)
        
        layout.addWidget(trouble_group)
        
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
        
        # Record type buttons (different color)
        record_button_style = """
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #0e6b0e;
            }
            QPushButton:pressed {
                background-color: #0c5a0c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        # Quick test buttons
        test_button_style = """
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
        """
        
        # Apply styles
        for btn in [self.forward_btn, self.reverse_btn, self.all_records_btn]:
            btn.setStyleSheet(main_button_style)
            
        for btn in [self.a_btn, self.mx_btn, self.txt_btn, self.ns_btn, self.cname_btn, self.aaaa_btn]:
            btn.setStyleSheet(record_button_style)
            
        for btn in [self.test_google_btn, self.test_ms_btn, self.test_github_btn, self.test_local_btn]:
            btn.setStyleSheet(test_button_style)
        
    def setup_connections(self):
        # Quick lookup connections
        self.forward_btn.clicked.connect(self.run_forward_lookup)
        self.reverse_btn.clicked.connect(self.run_reverse_lookup)
        self.all_records_btn.clicked.connect(self.run_all_records)
        
        # Record type connections - including new A record button
        self.a_btn.clicked.connect(self.run_a_lookup)
        self.mx_btn.clicked.connect(self.run_mx_lookup)
        self.txt_btn.clicked.connect(self.run_txt_lookup)
        self.ns_btn.clicked.connect(self.run_ns_lookup)
        self.cname_btn.clicked.connect(self.run_cname_lookup)
        self.aaaa_btn.clicked.connect(self.run_aaaa_lookup)
        
        # Test domain connections
        self.test_google_btn.clicked.connect(lambda: self.test_domain("google.com"))
        self.test_ms_btn.clicked.connect(lambda: self.test_domain("microsoft.com"))
        self.test_github_btn.clicked.connect(lambda: self.test_domain("github.com"))
        self.test_local_btn.clicked.connect(self.test_local_domain)
        
        # DNS tools connections
        self.dns_tools.result_ready.connect(self.handle_result)
        
        # DNS server selection
        self.dns_server_combo.currentTextChanged.connect(self.on_dns_server_changed)
        
        # Enter key connections
        self.quick_domain_edit.returnPressed.connect(self.run_forward_lookup)
        self.records_domain_edit.returnPressed.connect(self.run_all_records)
        
    def on_dns_server_changed(self, text):
            """Handle DNS server selection change"""
            if "Custom" in text:
                self.custom_dns_edit.setEnabled(True)
                self.custom_dns_edit.setFocus()
                # For custom DNS, we'll set it when the user enters a value
                self.custom_dns_edit.textChanged.connect(self.on_custom_dns_changed)
            else:
                self.custom_dns_edit.setEnabled(False)
                # Set the DNS server in the tools
                self.dns_tools.set_dns_server(text)

    def on_custom_dns_changed(self, text):
        """Handle custom DNS server input"""
        if text.strip():
            self.dns_tools.set_dns_server(text.strip())
            self.info(f"Custom DNS server set: {text.strip()}")
        
    def handle_result(self, message, level):
        if level == "SUCCESS":
            self.success(message)
        elif level == "ERROR":
            self.error(message)
        elif level == "WARNING":
            self.warning(message)
        else:
            self.info(message)
    
    def run_forward_lookup(self):
        domain = self.quick_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.forward_btn.setEnabled(False)
        self.info(f"Starting forward DNS lookup for {domain}...")
        
        self.dns_tools.forward_lookup(domain)
        
        # Re-enable button after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.forward_btn.setEnabled(True))
    
    def run_reverse_lookup(self):
        ip = self.quick_domain_edit.text().strip()
        if not ip:
            self.error("Please enter an IP address")
            return
            
        self.reverse_btn.setEnabled(False)
        self.info(f"Starting reverse DNS lookup for {ip}...")
        
        self.dns_tools.reverse_lookup(ip)
        
        # Re-enable button after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.reverse_btn.setEnabled(True))
    
    def run_all_records(self):
        domain = self.quick_domain_edit.text().strip() or self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.all_records_btn.setEnabled(False)
        self.info(f"Starting comprehensive DNS lookup for {domain}...")
        
        self.dns_tools.all_records_lookup(domain)
        
        # Re-enable button after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10000, lambda: self.all_records_btn.setEnabled(True))
    
    def run_a_lookup(self):
        """New A record lookup method"""
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.a_btn.setEnabled(False)
        self.dns_tools.a_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.a_btn.setEnabled(True))
    
    def run_mx_lookup(self):
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.mx_btn.setEnabled(False)
        self.dns_tools.mx_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.mx_btn.setEnabled(True))
    
    def run_txt_lookup(self):
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.txt_btn.setEnabled(False)
        self.dns_tools.txt_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.txt_btn.setEnabled(True))
    
    def run_ns_lookup(self):
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.ns_btn.setEnabled(False)
        self.dns_tools.ns_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.ns_btn.setEnabled(True))
    
    def run_cname_lookup(self):
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.cname_btn.setEnabled(False)
        self.dns_tools.cname_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.cname_btn.setEnabled(True))
    
    def run_aaaa_lookup(self):
        domain = self.records_domain_edit.text().strip()
        if not domain:
            self.error("Please enter a domain name")
            return
            
        self.aaaa_btn.setEnabled(False)
        self.dns_tools.aaaa_lookup(domain)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.aaaa_btn.setEnabled(True))
    
    def test_domain(self, domain):
        """Test a specific domain"""
        self.quick_domain_edit.setText(domain)
        self.records_domain_edit.setText(domain)
        self.run_all_records()
    
    def test_local_domain(self):
        """Test local domain detection"""
        import socket
        try:
            local_domain = socket.getfqdn()
            self.info(f"Detected local domain: {local_domain}")
            if '.' in local_domain:
                self.quick_domain_edit.setText(local_domain)
                self.run_forward_lookup()
            else:
                self.warning("Could not detect a valid local domain")
        except Exception as e:
            self.error(f"Error detecting local domain: {str(e)}")