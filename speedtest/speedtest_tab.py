# speedtest/speedtest_tab.py - UPDATED WITH ADVANCED LAN TESTING
import os
import socket
import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QLabel, QGridLayout,
                            QComboBox, QProgressBar, QSpinBox, QLCDNumber,
                            QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette
from core.base_tab import BaseTab
from speedtest.speedtest_tools import SpeedTestTools

# Import the new LAN testing tools
try:
    from speedtest.lan_speed_tools import LANSpeedTools
    LAN_TOOLS_AVAILABLE = True
except ImportError:
    LAN_TOOLS_AVAILABLE = False

class SpeedTestTab(BaseTab):
    def __init__(self, logger):
        super().__init__(logger)
        self.speedtest_tools = SpeedTestTools(logger)
        
        # Initialize LAN testing tools if available
        if LAN_TOOLS_AVAILABLE:
            self.lan_tools = LANSpeedTools(logger)
        
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0
        self.current_latency = 0.0
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Speed Display Section
        display_group = QGroupBox("Real-time Speed Display")
        display_layout = QGridLayout(display_group)
        
        # Download speed display
        display_layout.addWidget(QLabel("Download Speed:"), 0, 0)
        self.download_lcd = QLCDNumber(8)
        self.download_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.download_lcd.setStyleSheet("QLCDNumber { background-color: #1e1e1e; color: #00ff00; }")
        display_layout.addWidget(self.download_lcd, 0, 1)
        display_layout.addWidget(QLabel("Mbps"), 0, 2)
        
        # Upload speed display
        display_layout.addWidget(QLabel("Upload Speed:"), 1, 0)
        self.upload_lcd = QLCDNumber(8)
        self.upload_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.upload_lcd.setStyleSheet("QLCDNumber { background-color: #1e1e1e; color: #ff8800; }")
        display_layout.addWidget(self.upload_lcd, 1, 1)
        display_layout.addWidget(QLabel("Mbps"), 1, 2)
        
        # Latency display
        display_layout.addWidget(QLabel("Latency:"), 2, 0)
        self.latency_lcd = QLCDNumber(6)
        self.latency_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.latency_lcd.setStyleSheet("QLCDNumber { background-color: #1e1e1e; color: #0078d4; }")
        display_layout.addWidget(self.latency_lcd, 2, 1)
        display_layout.addWidget(QLabel("ms"), 2, 2)
        
        layout.addWidget(display_group)
        
        # Progress Section
        progress_group = QGroupBox("Test Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to test")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        # Internet Speed Test Section
        internet_group = QGroupBox("Internet Speed Test")
        internet_layout = QGridLayout(internet_group)
        
        # Speedtest method selection
        internet_layout.addWidget(QLabel("Test Method:"), 0, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "🎯 Speedtest.net CLI (Recommended)",
            "🔧 Built-in Test (Fallback)",
        ])
        internet_layout.addWidget(self.method_combo, 0, 1, 1, 2)
        
        internet_layout.addWidget(QLabel("Test Server:"), 1, 0)
        self.server_combo = QComboBox()
        self.server_combo.addItems([
            "Auto-select Best Server",
            "Cloudflare (Global CDN)",
            "Fast.com (Netflix)",
            "Google (Global)", 
            "Microsoft (Global)",
            "Custom Server..."
        ])
        internet_layout.addWidget(self.server_combo, 1, 1, 1, 2)
        
        internet_layout.addWidget(QLabel("Custom Server:"), 2, 0)
        self.custom_server_edit = QLineEdit()
        self.custom_server_edit.setPlaceholderText("https://example.com")
        self.custom_server_edit.setEnabled(False)
        internet_layout.addWidget(self.custom_server_edit, 2, 1, 1, 2)
        
        # Main test buttons
        self.official_test_btn = QPushButton("🚀 Official Speedtest")
        self.install_cli_btn = QPushButton("📥 Install CLI")
        self.test_cli_btn = QPushButton("🔧 Test CLI")
        self.latency_btn = QPushButton("Test Latency")
        self.list_servers_btn = QPushButton("List Servers")
        
        internet_layout.addWidget(self.official_test_btn, 3, 0)
        internet_layout.addWidget(self.install_cli_btn, 3, 1)
        internet_layout.addWidget(self.test_cli_btn, 3, 2)
        internet_layout.addWidget(self.latency_btn, 4, 0)
        internet_layout.addWidget(self.list_servers_btn, 4, 1)
        
        # Built-in test buttons (for fallback)
        self.download_btn = QPushButton("Test Download (Built-in)")
        self.upload_btn = QPushButton("Test Upload (Built-in)")
        self.comprehensive_btn = QPushButton("Comprehensive Test")
        
        internet_layout.addWidget(self.download_btn, 4, 2)
        internet_layout.addWidget(self.upload_btn, 5, 0)
        internet_layout.addWidget(self.comprehensive_btn, 5, 1, 1, 2)
        
        layout.addWidget(internet_group)
        
        # Advanced LAN Speed Test Section
        lan_group = QGroupBox("🏠 Advanced LAN Speed Test")
        lan_layout = QGridLayout(lan_group)
        
        lan_layout.addWidget(QLabel("Target IP:"), 0, 0)
        self.lan_ip_edit = QLineEdit()
        self.lan_ip_edit.setPlaceholderText("192.168.1.100")
        lan_layout.addWidget(self.lan_ip_edit, 0, 1)
        
        lan_layout.addWidget(QLabel("Port (optional):"), 0, 2)
        self.lan_port_spin = QSpinBox()
        self.lan_port_spin.setRange(1, 65535)
        self.lan_port_spin.setValue(12345)
        lan_layout.addWidget(self.lan_port_spin, 0, 3)
        
        # Advanced LAN test buttons
        if LAN_TOOLS_AVAILABLE:
            self.advanced_lan_btn = QPushButton("🚀 Advanced LAN Test")
            self.iperf3_guide_btn = QPushButton("📖 iperf3 Setup Guide")
            lan_layout.addWidget(self.advanced_lan_btn, 1, 0, 1, 2)
            lan_layout.addWidget(self.iperf3_guide_btn, 1, 2, 1, 2)
        else:
            # Fallback to basic LAN test
            self.lan_test_btn = QPushButton("Basic LAN Test")
            lan_layout.addWidget(self.lan_test_btn, 1, 0, 1, 2)
        
        self.detect_devices_btn = QPushButton("🔍 Detect Local Devices")
        self.ping_gateway_btn = QPushButton("📡 Ping Gateway")
        
        lan_layout.addWidget(self.detect_devices_btn, 2, 0, 1, 2)
        lan_layout.addWidget(self.ping_gateway_btn, 2, 2, 1, 2)
        
        layout.addWidget(lan_group)
        
        # LAN Testing Guide
        if LAN_TOOLS_AVAILABLE:
            guide_group = QGroupBox("🎯 LAN Speed Testing Guide")
            guide_layout = QVBoxLayout(guide_group)
            
            guide_text = QTextEdit()
            guide_text.setMaximumHeight(100)
            guide_text.setReadOnly(True)
            guide_text.setText(
                "Advanced LAN Testing Methods:\n"
                "• 🥇 iperf3: Most accurate (requires iperf3 -s on target)\n"
                "• 🌐 HTTP: Tests web servers (ports 80, 443, 8080)\n"
                "• 📁 FTP: Tests file servers (port 21)\n"
                "• 🗂️ SMB: Tests Windows file sharing (ports 445, 139)\n"
                "• 🔌 Socket: Basic throughput estimation\n"
                "Best results: Install iperf3 on both devices!"
            )
            guide_layout.addWidget(guide_text)
            layout.addWidget(guide_group)
        
        # Control Buttons Section
        control_group = QGroupBox("Test Controls")
        control_layout = QHBoxLayout(control_group)
        
        self.stop_btn = QPushButton("Stop Test")
        self.stop_btn.setEnabled(False)
        self.clear_results_btn = QPushButton("Clear Results")
        self.auto_test_btn = QPushButton("Auto Test All")
        
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.clear_results_btn)
        control_layout.addWidget(self.auto_test_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_group)
        
        # Speed Test Information Section
        info_group = QGroupBox("Speed Test Guide")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QTextEdit()
        info_text.setMaximumHeight(80)
        info_text.setReadOnly(True)
        info_text.setText(
            "Speed Test Guide:\n"
            "• Install Speedtest CLI for most accurate gigabit results\n"
            "• 'Official Speedtest' uses the same engine as speedtest.net\n"
            "• Built-in tests are fallbacks if CLI not available\n"
            "• Close other apps for best accuracy • Use 'List Servers' to find fastest server"
        )
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Style the buttons
        self.style_buttons()
        
        # Initialize displays
        self.update_speed_displays()
        
    def style_buttons(self):
        # Main test buttons
        test_button_style = """
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
        
        # Comprehensive test button (special style)
        comprehensive_button_style = """
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 12px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
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
        
        # LAN test button (advanced style)
        lan_button_style = """
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        # Control buttons
        control_button_style = """
            QPushButton {
                background-color: #d83b01;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
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
        
        # Apply styles
        for btn in [self.latency_btn, self.download_btn, self.upload_btn, 
                   self.list_servers_btn, self.test_cli_btn, self.detect_devices_btn,
                   self.ping_gateway_btn]:
            btn.setStyleSheet(test_button_style)
        
        self.official_test_btn.setStyleSheet(comprehensive_button_style)
        self.comprehensive_btn.setStyleSheet(comprehensive_button_style)
        
        # LAN testing buttons
        if LAN_TOOLS_AVAILABLE:
            self.advanced_lan_btn.setStyleSheet(lan_button_style)
            self.iperf3_guide_btn.setStyleSheet(test_button_style)
        else:
            if hasattr(self, 'lan_test_btn'):
                self.lan_test_btn.setStyleSheet(test_button_style)
        
        self.install_cli_btn.setStyleSheet("""
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
        """)
        
        for btn in [self.stop_btn, self.clear_results_btn, self.auto_test_btn]:
            btn.setStyleSheet(control_button_style)
        
    def setup_connections(self):
        # Server selection
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        
        # Test button connections
        self.official_test_btn.clicked.connect(self.run_official_speedtest)
        self.install_cli_btn.clicked.connect(self.show_install_instructions)
        self.test_cli_btn.clicked.connect(self.test_cli_manual)
        self.latency_btn.clicked.connect(self.test_latency)
        self.list_servers_btn.clicked.connect(self.list_servers)
        self.download_btn.clicked.connect(self.test_download)
        self.upload_btn.clicked.connect(self.test_upload)
        self.comprehensive_btn.clicked.connect(self.comprehensive_test)
        
        # LAN testing connections
        if LAN_TOOLS_AVAILABLE:
            self.advanced_lan_btn.clicked.connect(self.run_advanced_lan_test)
            self.iperf3_guide_btn.clicked.connect(self.show_iperf3_guide)
            # Setup LAN tools connections
            self.lan_tools.result_ready.connect(self.handle_result)
            self.lan_tools.progress_update.connect(self.update_progress)
            self.lan_tools.speed_update.connect(self.update_speed)
        else:
            if hasattr(self, 'lan_test_btn'):
                self.lan_test_btn.clicked.connect(self.test_basic_lan_speed)
        
        self.detect_devices_btn.clicked.connect(self.detect_local_devices)
        self.ping_gateway_btn.clicked.connect(self.ping_gateway)
        
        # Control button connections
        self.stop_btn.clicked.connect(self.stop_test)
        self.clear_results_btn.clicked.connect(self.clear_results)
        self.auto_test_btn.clicked.connect(self.auto_test_all)
        
        # Speedtest tools connections
        self.speedtest_tools.result_ready.connect(self.handle_result)
        self.speedtest_tools.progress_update.connect(self.update_progress)
        self.speedtest_tools.speed_update.connect(self.update_speed)
        
    def run_advanced_lan_test(self):
        """Run advanced LAN speed test with multiple methods"""
        target_ip = self.lan_ip_edit.text().strip()
        if not target_ip:
            self.error("Please enter target IP address")
            return
        
        port = self.lan_port_spin.value()
        
        self.info(f"🚀 Starting advanced LAN speed test to {target_ip}...")
        
        # Reset displays
        self.current_download_speed = 0.0
        self.update_speed_displays()
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting advanced LAN test...")
        self.set_test_buttons_enabled(False)
        self.stop_btn.setEnabled(True)
        
        if LAN_TOOLS_AVAILABLE:
            self.lan_tools.comprehensive_lan_test(target_ip, port)
        
        # Auto re-enable buttons after test
        QTimer.singleShot(30000, lambda: self.set_test_buttons_enabled(True))
        QTimer.singleShot(30000, lambda: self.stop_btn.setEnabled(False))
    
    def show_iperf3_guide(self):
        """Show iperf3 installation and setup guide"""
        if LAN_TOOLS_AVAILABLE:
            self.info("📖 Showing iperf3 setup guide...")
            self.lan_tools.install_iperf3_helper()
        else:
            self.info("💡 iperf3 is the best tool for LAN speed testing")
            self.info("Install: pip install iperf3 or download from iperf.fr")
    
    def test_basic_lan_speed(self):
        """Fallback basic LAN speed test"""
        target_ip = self.lan_ip_edit.text().strip()
        if not target_ip:
            self.error("Please enter target IP address")
            return
        
        port = self.lan_port_spin.value()
        
        self.info(f"Testing basic LAN connectivity to {target_ip}:{port}...")
        self.speedtest_tools.lan_speed_test(target_ip, port)
    
    def ping_gateway(self):
        """Ping the default gateway"""
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
                            self.lan_ip_edit.setText(gateway)
                            self.info(f"Found gateway: {gateway}")
                            self.speedtest_tools.ping_latency_test(gateway, 5)
                            return
            else:
                result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
                if result.returncode == 0:
                    gateway = result.stdout.split()[2]
                    self.lan_ip_edit.setText(gateway)
                    self.info(f"Found gateway: {gateway}")
                    self.speedtest_tools.ping_latency_test(gateway, 5)
                    return
                    
            self.error("Could not determine default gateway")
        except Exception as e:
            self.error(f"Error getting gateway: {str(e)}")
    
    def on_server_changed(self, text):
        """Handle server selection change"""
        if "Custom" in text:
            self.custom_server_edit.setEnabled(True)
            self.custom_server_edit.setFocus()
        else:
            self.custom_server_edit.setEnabled(False)
            
        self.info(f"Selected server: {text}")
    
    def get_selected_server(self):
        """Get currently selected server information"""
        servers = {
            "Auto-select Best Server": {"host": "speedtest.net", "url": "https://www.speedtest.net"},
            "Cloudflare (Global CDN)": {"host": "speed.cloudflare.com", "url": "https://speed.cloudflare.com"},
            "Fast.com (Netflix)": {"host": "fast.com", "url": "https://fast.com"},
            "Google (Global)": {"host": "www.google.com", "url": "https://www.google.com"},
            "Microsoft (Global)": {"host": "download.microsoft.com", "url": "https://download.microsoft.com"}
        }
        
        selected = self.server_combo.currentText()
        
        if "Custom" in selected and self.custom_server_edit.text():
            custom_url = self.custom_server_edit.text()
            from urllib.parse import urlparse
            parsed = urlparse(custom_url)
            return {"host": parsed.netloc or parsed.path, "url": custom_url}
        
        return servers.get(selected, servers["Google (Global)"])
    
    def update_speed_displays(self):
        """Update the LCD displays"""
        self.download_lcd.display(f"{self.current_download_speed:.1f}")
        self.upload_lcd.display(f"{self.current_upload_speed:.1f}")
        self.latency_lcd.display(f"{self.current_latency:.0f}")
        
    def handle_result(self, message, level):
        if level == "SUCCESS":
            self.success(message)
        elif level == "ERROR":
            self.error(message)
        elif level == "WARNING":
            self.warning(message)
        else:
            self.info(message)
    
    def update_progress(self, percentage, status):
        """Update progress bar and status"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(status)
        
        # Update button states during test
        if percentage > 0 and percentage < 100:
            self.stop_btn.setEnabled(True)
            self.set_test_buttons_enabled(False)
        elif percentage >= 100:
            self.stop_btn.setEnabled(False)
            self.set_test_buttons_enabled(True)
            self.progress_label.setText("Test completed")
    
    def update_speed(self, speed, test_type):
        """Update speed displays based on test type"""
        if test_type == "download":
            self.current_download_speed = speed
        elif test_type == "upload":
            self.current_upload_speed = speed
        elif test_type == "lan":
            # For LAN tests, show as download speed
            self.current_download_speed = speed
        elif test_type == "latency":
            self.current_latency = speed
            
        self.update_speed_displays()
    
    def set_test_buttons_enabled(self, enabled):
        """Enable/disable test buttons"""
        self.official_test_btn.setEnabled(enabled)
        self.latency_btn.setEnabled(enabled)
        self.list_servers_btn.setEnabled(enabled)
        self.download_btn.setEnabled(enabled)
        self.upload_btn.setEnabled(enabled)
        self.comprehensive_btn.setEnabled(enabled)
        
        if LAN_TOOLS_AVAILABLE:
            self.advanced_lan_btn.setEnabled(enabled)
        else:
            if hasattr(self, 'lan_test_btn'):
                self.lan_test_btn.setEnabled(enabled)
                
        self.detect_devices_btn.setEnabled(enabled)
        self.ping_gateway_btn.setEnabled(enabled)
        self.auto_test_btn.setEnabled(enabled)
    
    # Keep all the existing methods from the original file...
    def run_official_speedtest(self):
        """Run official speedtest.net CLI test"""
        self.info("🚀 Starting official Speedtest.net test...")
        
        # Reset displays
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0
        self.current_latency = 0.0
        self.update_speed_displays()
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting official speedtest...")
        self.set_test_buttons_enabled(False)
        self.stop_btn.setEnabled(True)
        
        self.speedtest_tools.speedtest_cli_test()
        
        # Auto re-enable buttons after test
        QTimer.singleShot(45000, lambda: self.set_test_buttons_enabled(True))
        QTimer.singleShot(45000, lambda: self.stop_btn.setEnabled(False))
    
    def test_cli_manual(self):
        """Test speedtest CLI manually to debug issues"""
        self.speedtest_tools.test_cli_manual()
    
    def show_install_instructions(self):
        """Show speedtest CLI installation instructions"""
        self.speedtest_tools.show_install_instructions()
    
    def list_servers(self):
        """List available speedtest servers"""
        self.info("🔍 Listing available speedtest servers...")
        self.speedtest_tools.list_speedtest_servers()
    
    def test_latency(self):
        """Test latency to selected server"""
        server = self.get_selected_server()
        self.info(f"Starting latency test to {server['host']}...")
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Testing latency...")
        self.set_test_buttons_enabled(False)
        self.stop_btn.setEnabled(True)
        
        self.speedtest_tools.ping_latency_test(server['host'], 10)
        
        # Auto re-enable buttons after test
        QTimer.singleShot(15000, lambda: self.set_test_buttons_enabled(True))
        QTimer.singleShot(15000, lambda: self.stop_btn.setEnabled(False))
    
    def test_download(self):
        """Test download speed using built-in method"""
        self.speedtest_tools.test_download()
    
    def test_upload(self):
        """Test upload speed using built-in method"""
        self.speedtest_tools.test_upload()
    
    def comprehensive_test(self):
        """Run comprehensive speed test"""
        server = self.get_selected_server()
        self.info("Starting comprehensive speed test...")
        
        # Reset displays
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0
        self.current_latency = 0.0
        self.update_speed_displays()
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting comprehensive test...")
        self.set_test_buttons_enabled(False)
        self.stop_btn.setEnabled(True)
        
        self.speedtest_tools.comprehensive_speed_test(server)
        
        # Auto re-enable buttons after comprehensive test
        QTimer.singleShot(45000, lambda: self.set_test_buttons_enabled(True))
        QTimer.singleShot(45000, lambda: self.stop_btn.setEnabled(False))
    
    def detect_local_devices(self):
        """Detect devices on local network"""
        self.info("Scanning for local devices...")
        
        import subprocess
        import threading
        
        def _scan_network():
            try:
                # Get local network range
                result = subprocess.run(["ipconfig" if os.name == "nt" else "ip", "route"], 
                                      capture_output=True, text=True)
                
                # Simple network scan (this is a basic implementation)
                import socket
                import ipaddress
                
                # Try to determine local network
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                
                self.info(f"Local IP: {local_ip}")
                
                # Scan common local IPs
                network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
                found_devices = []
                
                for ip in list(network.hosts())[:20]:  # Scan first 20 IPs
                    try:
                        socket.create_connection((str(ip), 80), timeout=1).close()
                        found_devices.append(str(ip))
                    except:
                        pass
                
                if found_devices:
                    self.success(f"Found devices: {', '.join(found_devices)}")
                    if found_devices and not self.lan_ip_edit.text():
                        self.lan_ip_edit.setText(found_devices[0])
                else:
                    self.warning("No devices found on local network")
                    
            except Exception as e:
                self.error(f"Network scan error: {str(e)}")
        
        thread = threading.Thread(target=_scan_network)
        thread.daemon = True
        thread.start()
    
    def auto_test_all(self):
        """Run all tests automatically"""
        self.info("Starting automatic test sequence...")
        
        # Reset displays
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0
        self.current_latency = 0.0
        self.update_speed_displays()
        
        self.set_test_buttons_enabled(False)
        self.stop_btn.setEnabled(True)
        
        # Run tests in sequence
        self.test_latency()
        QTimer.singleShot(20000, self.test_download)
        QTimer.singleShot(40000, self.test_upload)
        
        # Re-enable after all tests
        QTimer.singleShot(65000, lambda: self.set_test_buttons_enabled(True))
        QTimer.singleShot(65000, lambda: self.stop_btn.setEnabled(False))
    
    def stop_test(self):
        """Stop current test safely"""
        # Stop speedtest tools
        self.speedtest_tools.stop_test()
        
        # Stop LAN tools if available
        if LAN_TOOLS_AVAILABLE:
            self.lan_tools.stop_test()
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.progress_label.setText("Test stopped")
        self.stop_btn.setEnabled(False)
        self.set_test_buttons_enabled(True)
        self.warning("Test stopped by user")
    
    def clear_results(self):
        """Clear all results and reset displays"""
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0
        self.current_latency = 0.0
        self.update_speed_displays()
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ready to test")
        
        self.info("Speed test results cleared")