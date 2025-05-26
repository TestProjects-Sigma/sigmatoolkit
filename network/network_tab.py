# network/network_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QSpinBox,
                            QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from core.base_tab import BaseTab
from network.network_tools import NetworkTools

class NetworkTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.network_tools = NetworkTools(logger)
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Ping Section
        ping_group = QGroupBox("Ping Test")
        ping_layout = QGridLayout(ping_group)
        
        ping_layout.addWidget(QLabel("Host:"), 0, 0)
        self.ping_host_edit = QLineEdit()
        self.ping_host_edit.setPlaceholderText("Enter hostname or IP address")
        ping_layout.addWidget(self.ping_host_edit, 0, 1)
        
        ping_layout.addWidget(QLabel("Count:"), 0, 2)
        self.ping_count_spin = QSpinBox()
        self.ping_count_spin.setRange(1, 100)
        self.ping_count_spin.setValue(4)
        ping_layout.addWidget(self.ping_count_spin, 0, 3)
        
        self.ping_btn = QPushButton("Ping")
        self.ping_btn.setMinimumHeight(30)
        ping_layout.addWidget(self.ping_btn, 0, 4)
        
        layout.addWidget(ping_group)
        
        # Traceroute Section
        trace_group = QGroupBox("Traceroute")
        trace_layout = QGridLayout(trace_group)
        
        trace_layout.addWidget(QLabel("Host:"), 0, 0)
        self.trace_host_edit = QLineEdit()
        self.trace_host_edit.setPlaceholderText("Enter hostname or IP address")
        trace_layout.addWidget(self.trace_host_edit, 0, 1)
        
        self.trace_btn = QPushButton("Traceroute")
        self.trace_btn.setMinimumHeight(30)
        trace_layout.addWidget(self.trace_btn, 0, 2)
        
        layout.addWidget(trace_group)
        
        # Port Scan Section
        port_group = QGroupBox("Port Scanner")
        port_layout = QGridLayout(port_group)
        
        port_layout.addWidget(QLabel("Host:"), 0, 0)
        self.port_host_edit = QLineEdit()
        self.port_host_edit.setPlaceholderText("Enter hostname or IP address")
        port_layout.addWidget(self.port_host_edit, 0, 1)
        
        port_layout.addWidget(QLabel("Ports:"), 0, 2)
        self.ports_edit = QLineEdit()
        self.ports_edit.setPlaceholderText("e.g., 80,443,22 or 1-1000")
        port_layout.addWidget(self.ports_edit, 0, 3)
        
        self.port_scan_btn = QPushButton("Scan Ports")
        self.port_scan_btn.setMinimumHeight(30)
        port_layout.addWidget(self.port_scan_btn, 0, 4)
        
        layout.addWidget(port_group)
        
        # DNS Lookup Section
        dns_group = QGroupBox("DNS Lookup")
        dns_layout = QGridLayout(dns_group)
        
        dns_layout.addWidget(QLabel("Host:"), 0, 0)
        self.dns_host_edit = QLineEdit()
        self.dns_host_edit.setPlaceholderText("Enter hostname")
        dns_layout.addWidget(self.dns_host_edit, 0, 1)
        
        self.dns_btn = QPushButton("DNS Lookup")
        self.dns_btn.setMinimumHeight(30)
        dns_layout.addWidget(self.dns_btn, 0, 2)
        
        layout.addWidget(dns_group)
        
        # Quick Actions Section
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_group)
        
        self.quick_google_btn = QPushButton("Ping Google DNS")
        self.quick_cloudflare_btn = QPushButton("Ping Cloudflare DNS")
        self.quick_local_btn = QPushButton("Ping Gateway")
        
        quick_layout.addWidget(self.quick_google_btn)
        quick_layout.addWidget(self.quick_cloudflare_btn)
        quick_layout.addWidget(self.quick_local_btn)
        quick_layout.addStretch()
        
        layout.addWidget(quick_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Style the buttons
        self.style_buttons()
        
    def style_buttons(self):
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
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
        
        for btn in [self.ping_btn, self.trace_btn, self.port_scan_btn, 
                   self.dns_btn, self.quick_google_btn, self.quick_cloudflare_btn, 
                   self.quick_local_btn]:
            btn.setStyleSheet(button_style)
        
    def setup_connections(self):
        # Button connections
        self.ping_btn.clicked.connect(self.run_ping)
        self.trace_btn.clicked.connect(self.run_traceroute)
        self.port_scan_btn.clicked.connect(self.run_port_scan)
        self.dns_btn.clicked.connect(self.run_dns_lookup)
        
        # Quick action connections
        self.quick_google_btn.clicked.connect(lambda: self.quick_ping("8.8.8.8"))
        self.quick_cloudflare_btn.clicked.connect(lambda: self.quick_ping("1.1.1.1"))
        self.quick_local_btn.clicked.connect(self.ping_gateway)
        
        # Network tools connections
        self.network_tools.result_ready.connect(self.handle_result)
        
        # Enter key connections
        self.ping_host_edit.returnPressed.connect(self.run_ping)
        self.trace_host_edit.returnPressed.connect(self.run_traceroute)
        self.dns_host_edit.returnPressed.connect(self.run_dns_lookup)
        
    def handle_result(self, message, level):
        if level == "SUCCESS":
            self.success(message)
        elif level == "ERROR":
            self.error(message)
        elif level == "WARNING":
            self.warning(message)
        else:
            self.info(message)
    
    def run_ping(self):
        host = self.ping_host_edit.text().strip()
        if not host:
            self.error("Please enter a host to ping")
            return
            
        count = self.ping_count_spin.value()
        self.ping_btn.setEnabled(False)
        self.info(f"Starting ping test to {host}...")
        
        self.network_tools.ping(host, count)
        
        # Re-enable button after a delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.ping_btn.setEnabled(True))
    
    def run_traceroute(self):
        host = self.trace_host_edit.text().strip()
        if not host:
            self.error("Please enter a host for traceroute")
            return
            
        self.trace_btn.setEnabled(False)
        self.info(f"Starting traceroute to {host}...")
        
        self.network_tools.traceroute(host)
        
        # Re-enable button after a delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10000, lambda: self.trace_btn.setEnabled(True))
    
    def run_port_scan(self):
        host = self.port_host_edit.text().strip()
        ports = self.ports_edit.text().strip()
        
        if not host:
            self.error("Please enter a host to scan")
            return
        if not ports:
            self.error("Please enter ports to scan")
            return
            
        self.port_scan_btn.setEnabled(False)
        self.info(f"Starting port scan on {host}...")
        
        self.network_tools.port_scan(host, ports)
        
        # Re-enable button after a delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(15000, lambda: self.port_scan_btn.setEnabled(True))
    
    def run_dns_lookup(self):
        host = self.dns_host_edit.text().strip()
        if not host:
            self.error("Please enter a host for DNS lookup")
            return
            
        self.dns_btn.setEnabled(False)
        self.info(f"Starting DNS lookup for {host}...")
        
        self.network_tools.dns_lookup(host)
        
        # Re-enable button after a delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.dns_btn.setEnabled(True))
    
    def quick_ping(self, ip):
        self.ping_host_edit.setText(ip)
        self.run_ping()
    
    def ping_gateway(self):
        import subprocess
        import platform
        
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ipconfig"], capture_output=True, text=True)
                # Extract default gateway from ipconfig output
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line:
                        gateway = line.split(':')[-1].strip()
                        if gateway and gateway != '':
                            self.ping_host_edit.setText(gateway)
                            self.run_ping()
                            return
            else:
                result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
                if result.returncode == 0:
                    gateway = result.stdout.split()[2]
                    self.ping_host_edit.setText(gateway)
                    self.run_ping()
                    return
                    
            self.error("Could not determine default gateway")
        except Exception as e:
            self.error(f"Error getting gateway: {str(e)}")