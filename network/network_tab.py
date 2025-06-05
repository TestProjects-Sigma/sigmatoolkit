# network/network_tab.py - Updated with System Network Information
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QSpinBox,
                            QGridLayout, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from core.base_tab import BaseTab
from network.network_tools import NetworkTools
import socket
import subprocess
import platform
import requests
import threading

class SystemInfoWorker(QThread):
    """Worker thread to gather system network information"""
    info_ready = pyqtSignal(dict)
    
    def run(self):
        info = {}
        try:
            # Get local IP and subnet
            info.update(self.get_local_network_info())
            # Get external IP
            info['external_ip'] = self.get_external_ip()
            # Get default gateway
            info['gateway'] = self.get_default_gateway()
            # Get DNS servers
            info['dns_servers'] = self.get_dns_servers()
            # Get network interfaces
            info['interfaces'] = self.get_network_interfaces()
        except Exception as e:
            info['error'] = str(e)
        
        self.info_ready.emit(info)
    
    def get_local_network_info(self):
        """Get local IP address and subnet information"""
        try:
            # Connect to a remote address to determine the local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            
            hostname = socket.gethostname()
            
            return {
                'local_ip': local_ip,
                'hostname': hostname,
                'subnet': self.calculate_subnet(local_ip)
            }
        except Exception as e:
            return {'local_ip': 'Unknown', 'hostname': 'Unknown', 'subnet': 'Unknown'}
    
    def calculate_subnet(self, ip):
        """Calculate likely subnet based on IP class"""
        octets = ip.split('.')
        if octets[0] == '192' and octets[1] == '168':
            return f"192.168.{octets[2]}.0/24"
        elif octets[0] == '10':
            return "10.0.0.0/8"
        elif octets[0] == '172' and 16 <= int(octets[1]) <= 31:
            return f"172.{octets[1]}.0.0/16"
        else:
            return f"{'.'.join(octets[:3])}.0/24"
    
    def get_external_ip(self):
        """Get external/public IP address"""
        try:
            # Try multiple services for reliability
            services = [
                'https://api.ipify.org',
                'https://checkip.amazonaws.com',
                'https://icanhazip.com'
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue
            
            return "Unable to determine"
        except:
            return "Unable to determine"
    
    def get_default_gateway(self):
        """Get default gateway IP"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line:
                        gateway = line.split(':')[-1].strip()
                        if gateway and gateway != '':
                            return gateway
            else:
                result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout.split()[2]
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_dns_servers(self):
        """Get DNS server information"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["nslookup", "google.com"], capture_output=True, text=True, timeout=10)
                dns_servers = []
                for line in result.stdout.split('\n'):
                    if 'Server:' in line:
                        dns = line.split(':')[-1].strip()
                        if dns:
                            dns_servers.append(dns)
                return dns_servers[:2] if dns_servers else ["Unknown"]
            else:
                with open('/etc/resolv.conf', 'r') as f:
                    dns_servers = []
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
                    return dns_servers[:2] if dns_servers else ["Unknown"]
        except:
            return ["Unknown"]
    
    def get_network_interfaces(self):
        """Get network interface information"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=10)
                # Parse active interfaces
                interfaces = []
                current_interface = None
                for line in result.stdout.split('\n'):
                    if 'adapter' in line.lower() and ':' in line:
                        current_interface = line.split(':')[0].strip()
                    elif 'IPv4 Address' in line and current_interface:
                        interfaces.append(current_interface)
                        current_interface = None
                return interfaces[:3] if interfaces else ["Unknown"]
            else:
                result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, timeout=10)
                interfaces = []
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'inet ' in line:
                        interface = line.split(':')[1].strip().split()[0]
                        if interface not in interfaces:
                            interfaces.append(interface)
                return interfaces[:3] if interfaces else ["Unknown"]
        except:
            return ["Unknown"]

class NetworkTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.network_tools = NetworkTools(logger)
        self.system_info = {}
        self.init_ui()
        self.setup_connections()
        self.load_system_info()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # System Network Information Section (NEW)
        system_group = QGroupBox("🖥️ System Network Information")
        system_layout = QVBoxLayout(system_group)
        
        # Create info display area
        self.system_info_text = QTextEdit()
        self.system_info_text.setMaximumHeight(150)
        self.system_info_text.setFont(QFont("Consolas", 10))
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                color: #495057;
            }
        """)
        self.system_info_text.setText("🔄 Loading system network information...")
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh Network Info")
        self.refresh_btn.setMaximumWidth(200)
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addStretch()
        
        system_layout.addWidget(self.system_info_text)
        system_layout.addLayout(refresh_layout)
        
        layout.addWidget(system_group)
        
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
        
        refresh_style = """
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
        """
        
        for btn in [self.ping_btn, self.trace_btn, self.port_scan_btn, 
                   self.dns_btn, self.quick_google_btn, self.quick_cloudflare_btn, 
                   self.quick_local_btn]:
            btn.setStyleSheet(button_style)
        
        self.refresh_btn.setStyleSheet(refresh_style)
        
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
        
        # Refresh button
        self.refresh_btn.clicked.connect(self.load_system_info)
        
        # Network tools connections
        self.network_tools.result_ready.connect(self.handle_result)
        
        # Enter key connections
        self.ping_host_edit.returnPressed.connect(self.run_ping)
        self.trace_host_edit.returnPressed.connect(self.run_traceroute)
        self.dns_host_edit.returnPressed.connect(self.run_dns_lookup)
        
    def load_system_info(self):
        """Load system network information in background thread"""
        self.system_info_text.setText("🔄 Loading system network information...")
        self.refresh_btn.setEnabled(False)
        
        self.info_worker = SystemInfoWorker()
        self.info_worker.info_ready.connect(self.update_system_info)
        self.info_worker.start()
        
    def update_system_info(self, info):
        """Update the system info display"""
        self.system_info = info
        self.refresh_btn.setEnabled(True)
        
        if 'error' in info:
            self.system_info_text.setText(f"❌ Error loading system information: {info['error']}")
            return
        
        # Format the information nicely
        info_text = f"""💻 Computer: {info.get('hostname', 'Unknown')}
🌐 Local IP: {info.get('local_ip', 'Unknown')}
📡 Subnet: {info.get('subnet', 'Unknown')}
🚪 Gateway: {info.get('gateway', 'Unknown')}
🌍 External IP: {info.get('external_ip', 'Loading...')}
🔍 DNS Servers: {', '.join(info.get('dns_servers', ['Unknown']))}
🔌 Active Interfaces: {', '.join(info.get('interfaces', ['Unknown']))}"""
        
        self.system_info_text.setText(info_text)
        
        # Log the info to the main output as well
        self.info(f"System Network Summary - Local: {info.get('local_ip', 'Unknown')}, External: {info.get('external_ip', 'Unknown')}, Gateway: {info.get('gateway', 'Unknown')}")

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
        gateway = self.system_info.get('gateway', 'Unknown')
        if gateway and gateway != 'Unknown':
            self.ping_host_edit.setText(gateway)
            self.run_ping()
        else:
            self.error("Gateway not available - try refreshing network info first")