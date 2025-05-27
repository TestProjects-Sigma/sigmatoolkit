# speedtest/lan_speed_tools.py - ADVANCED LAN TESTING
import threading
import time
import socket
import subprocess
import json
import os
import platform
import tempfile
import urllib.request
import urllib.error
from PyQt5.QtCore import QObject, pyqtSignal

class LANSpeedTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    progress_update = pyqtSignal(int, str)  # progress percentage, status
    speed_update = pyqtSignal(float, str)  # speed value, test type
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.test_running = False
        
    def comprehensive_lan_test(self, target_ip, port=None):
        """Comprehensive LAN speed test with multiple methods"""
        def _comprehensive_test():
            try:
                self.test_running = True
                self.result_ready.emit("🏠 Starting Comprehensive LAN Speed Test", "INFO")
                self.result_ready.emit(f"Target: {target_ip}", "INFO")
                self.result_ready.emit("=" * 50, "INFO")
                
                # Method 1: Check for iperf3 availability
                self.progress_update.emit(10, "Checking for iperf3...")
                iperf_available = self._check_iperf3_availability(target_ip)
                
                # Method 2: HTTP download test (if web server available)
                self.progress_update.emit(30, "Testing HTTP download...")
                http_speed = self._test_http_download(target_ip)
                
                # Method 3: FTP test (if FTP server available)
                self.progress_update.emit(50, "Testing FTP access...")
                ftp_speed = self._test_ftp_access(target_ip)
                
                # Method 4: SMB/CIFS test (Windows file sharing)
                self.progress_update.emit(70, "Testing SMB/File sharing...")
                smb_speed = self._test_smb_access(target_ip)
                
                # Method 5: Raw socket throughput test
                self.progress_update.emit(85, "Testing raw socket throughput...")
                socket_speed = self._test_raw_socket_throughput(target_ip, port or 12345)
                
                # Compile results
                self.progress_update.emit(95, "Compiling results...")
                self._compile_lan_results(target_ip, {
                    'iperf': iperf_available,
                    'http': http_speed,
                    'ftp': ftp_speed, 
                    'smb': smb_speed,
                    'socket': socket_speed
                })
                
                self.progress_update.emit(100, "LAN test completed")
                
            except Exception as e:
                self.result_ready.emit(f"❌ Comprehensive LAN test error: {str(e)}", "ERROR")
            finally:
                self.test_running = False
                
        thread = threading.Thread(target=_comprehensive_test)
        thread.daemon = True
        thread.start()
    
    def _check_iperf3_availability(self, target_ip):
        """Check if iperf3 is available locally and on target"""
        try:
            # Check if iperf3 is installed locally
            local_iperf = False
            try:
                result = subprocess.run(["iperf3", "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    local_iperf = True
                    self.result_ready.emit("✅ iperf3 found locally", "SUCCESS")
                else:
                    self.result_ready.emit("❌ iperf3 not installed locally", "WARNING")
            except FileNotFoundError:
                self.result_ready.emit("❌ iperf3 not installed locally", "WARNING")
                self.result_ready.emit("💡 Install with: pip install iperf3 (or download from iperf.fr)", "INFO")
            
            if local_iperf:
                # Test if target has iperf3 server running
                try:
                    # Try to connect to default iperf3 port (5201)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((target_ip, 5201))
                    sock.close()
                    
                    if result == 0:
                        self.result_ready.emit(f"✅ iperf3 server detected on {target_ip}:5201", "SUCCESS")
                        return self._run_iperf3_test(target_ip)
                    else:
                        self.result_ready.emit(f"❌ No iperf3 server on {target_ip}:5201", "WARNING")
                        self.result_ready.emit("💡 Start server on target: iperf3 -s", "INFO")
                        
                except Exception as e:
                    self.result_ready.emit(f"Could not test iperf3 server: {str(e)}", "WARNING")
            
            return None
            
        except Exception as e:
            self.result_ready.emit(f"iperf3 check error: {str(e)}", "ERROR")
            return None
    
    def _run_iperf3_test(self, target_ip):
        """Run actual iperf3 test"""
        try:
            self.result_ready.emit("🚀 Running iperf3 LAN speed test...", "INFO")
            
            # Run iperf3 test
            cmd = ["iperf3", "-c", target_ip, "-J", "-t", "10"]  # 10 second test, JSON output
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse JSON results
                data = json.loads(result.stdout)
                
                # Extract speeds
                sent_mbps = data["end"]["sum_sent"]["bits_per_second"] / 1000000
                received_mbps = data["end"]["sum_received"]["bits_per_second"] / 1000000
                
                self.result_ready.emit("🎯 iperf3 Results:", "SUCCESS")
                self.result_ready.emit(f"  Upload: {sent_mbps:.1f} Mbps", "SUCCESS")
                self.result_ready.emit(f"  Download: {received_mbps:.1f} Mbps", "SUCCESS")
                
                # Update speed display
                self.speed_update.emit(received_mbps, "lan")
                
                return {
                    'upload': sent_mbps,
                    'download': received_mbps,
                    'method': 'iperf3'
                }
            else:
                self.result_ready.emit(f"iperf3 test failed: {result.stderr}", "ERROR")
                return None
                
        except json.JSONDecodeError:
            self.result_ready.emit("Could not parse iperf3 results", "ERROR")
            return None
        except Exception as e:
            self.result_ready.emit(f"iperf3 test error: {str(e)}", "ERROR")
            return None
    
    def _test_http_download(self, target_ip):
        """Test HTTP download speed from target"""
        try:
            # Try common HTTP ports
            http_ports = [80, 8080, 8000, 443]
            
            for port in http_ports:
                try:
                    # Test if HTTP server is available
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((target_ip, port))
                    sock.close()
                    
                    if result == 0:
                        # Try to download something
                        protocol = "https" if port == 443 else "http"
                        test_urls = [
                            f"{protocol}://{target_ip}:{port}/",
                            f"{protocol}://{target_ip}:{port}/index.html",
                            f"{protocol}://{target_ip}:{port}/test"
                        ]
                        
                        for url in test_urls:
                            try:
                                start_time = time.time()
                                
                                # Try to download with timeout
                                response = urllib.request.urlopen(url, timeout=5)
                                data = response.read()
                                
                                download_time = time.time() - start_time
                                data_size = len(data)
                                
                                if data_size > 0 and download_time > 0:
                                    # Calculate speed (convert bytes to Mbps)
                                    speed_mbps = (data_size * 8) / (download_time * 1000000)
                                    
                                    self.result_ready.emit(f"✅ HTTP server found on port {port}", "SUCCESS")
                                    self.result_ready.emit(f"  Downloaded {data_size} bytes in {download_time:.2f}s", "INFO")
                                    self.result_ready.emit(f"  Speed: ~{speed_mbps:.1f} Mbps", "INFO")
                                    
                                    return {
                                        'speed': speed_mbps,
                                        'port': port,
                                        'size': data_size,
                                        'time': download_time
                                    }
                                    
                            except urllib.error.HTTPError as e:
                                if e.code == 404:
                                    continue  # Try next URL
                                else:
                                    break
                            except Exception:
                                continue
                                
                except Exception:
                    continue
            
            self.result_ready.emit("❌ No accessible HTTP servers found", "WARNING")
            return None
            
        except Exception as e:
            self.result_ready.emit(f"HTTP test error: {str(e)}", "ERROR")
            return None
    
    def _test_ftp_access(self, target_ip):
        """Test FTP access and speed"""
        try:
            # Test FTP port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((target_ip, 21))
            sock.close()
            
            if result == 0:
                self.result_ready.emit(f"✅ FTP server detected on {target_ip}:21", "SUCCESS")
                
                # Try anonymous FTP connection
                try:
                    import ftplib
                    
                    ftp = ftplib.FTP()
                    ftp.connect(target_ip, timeout=5)
                    ftp.login()  # Anonymous login
                    
                    # Try to list directory (basic speed test)
                    start_time = time.time()
                    file_list = ftp.nlst()
                    list_time = time.time() - start_time
                    
                    ftp.quit()
                    
                    self.result_ready.emit(f"  Anonymous FTP access: ✅", "SUCCESS")
                    self.result_ready.emit(f"  Directory listing: {len(file_list)} files in {list_time:.2f}s", "INFO")
                    
                    return {
                        'accessible': True,
                        'files': len(file_list),
                        'list_time': list_time
                    }
                    
                except Exception as e:
                    self.result_ready.emit(f"  FTP access failed: {str(e)}", "WARNING")
                    return {'accessible': False}
            else:
                self.result_ready.emit("❌ No FTP server found", "INFO")
                return None
                
        except Exception as e:
            self.result_ready.emit(f"FTP test error: {str(e)}", "ERROR")
            return None
    
    def _test_smb_access(self, target_ip):
        """Test SMB/CIFS file sharing"""
        try:
            # Test SMB ports
            smb_ports = [445, 139]  # SMB over TCP, NetBIOS
            
            for port in smb_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((target_ip, port))
                    sock.close()
                    
                    if result == 0:
                        self.result_ready.emit(f"✅ SMB port {port} is open", "SUCCESS")
                        
                        # Try to get hostname via NetBIOS (Windows)
                        if platform.system().lower() == "windows":
                            try:
                                # Use nbtstat to get NetBIOS name
                                cmd = ["nbtstat", "-A", target_ip]
                                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                                
                                if result.returncode == 0 and "Name" in result.stdout:
                                    self.result_ready.emit("  Windows file sharing detected", "SUCCESS")
                                    return {'smb_available': True, 'port': port}
                                    
                            except Exception:
                                pass
                        
                        return {'smb_available': True, 'port': port}
                        
                except Exception:
                    continue
            
            self.result_ready.emit("❌ No SMB/file sharing detected", "INFO")
            return None
            
        except Exception as e:
            self.result_ready.emit(f"SMB test error: {str(e)}", "ERROR")
            return None
    
    def _test_raw_socket_throughput(self, target_ip, port):
        """Test raw socket throughput"""
        try:
            # Test if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            if result == 0:
                self.result_ready.emit(f"✅ Port {port} is accessible", "SUCCESS")
                
                # Multiple connection speed test
                connection_times = []
                data_sizes = []
                
                for i in range(5):
                    try:
                        start_time = time.time()
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((target_ip, port))
                        
                        # Try to send/receive some data
                        test_data = b"SPEED_TEST_" + str(i).encode() + b"_" * 100
                        sock.send(test_data)
                        
                        # Try to receive response (may timeout, that's ok)
                        try:
                            response = sock.recv(1024)
                            data_sizes.append(len(response))
                        except:
                            data_sizes.append(len(test_data))
                        
                        connection_time = time.time() - start_time
                        connection_times.append(connection_time)
                        
                        sock.close()
                        time.sleep(0.1)
                        
                    except Exception:
                        pass
                
                if connection_times:
                    avg_time = sum(connection_times) / len(connection_times)
                    avg_size = sum(data_sizes) / len(data_sizes) if data_sizes else 100
                    
                    # Estimate speed based on connection performance
                    estimated_speed = (avg_size * 8) / (avg_time * 1000000)  # Convert to Mbps
                    
                    self.result_ready.emit(f"  Average connection time: {avg_time:.3f}s", "INFO")
                    self.result_ready.emit(f"  Estimated throughput: ~{estimated_speed:.1f} Mbps", "INFO")
                    
                    return {
                        'speed': estimated_speed,
                        'avg_time': avg_time,
                        'connections': len(connection_times)
                    }
            else:
                self.result_ready.emit(f"❌ Port {port} is not accessible", "WARNING")
                return None
                
        except Exception as e:
            self.result_ready.emit(f"Socket throughput test error: {str(e)}", "ERROR")
            return None
    
    def _compile_lan_results(self, target_ip, results):
        """Compile and display comprehensive LAN test results"""
        try:
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("🏠 COMPREHENSIVE LAN TEST RESULTS", "SUCCESS")
            self.result_ready.emit("=" * 50, "INFO")
            self.result_ready.emit(f"Target: {target_ip}", "INFO")
            self.result_ready.emit("", "INFO")
            
            # Best speed found
            best_speed = 0
            best_method = "None"
            
            # iperf3 results
            if results['iperf']:
                iperf_data = results['iperf']
                speed = max(iperf_data['upload'], iperf_data['download'])
                if speed > best_speed:
                    best_speed = speed
                    best_method = "iperf3 (Most Accurate)"
                self.result_ready.emit("🎯 iperf3 Test: ✅ PASSED", "SUCCESS")
                self.result_ready.emit(f"  This is the most accurate LAN speed measurement", "SUCCESS")
            else:
                self.result_ready.emit("🎯 iperf3 Test: ❌ Not Available", "WARNING")
                self.result_ready.emit("  💡 For best results, install iperf3 on both devices", "INFO")
            
            # HTTP results
            if results['http']:
                http_data = results['http']
                if http_data['speed'] > best_speed:
                    best_speed = http_data['speed']
                    best_method = "HTTP Download"
                self.result_ready.emit("🌐 HTTP Test: ✅ PASSED", "SUCCESS")
                self.result_ready.emit(f"  Web server found on port {http_data['port']}", "INFO")
            else:
                self.result_ready.emit("🌐 HTTP Test: ❌ No web server", "INFO")
            
            # FTP results
            if results['ftp']:
                self.result_ready.emit("📁 FTP Test: ✅ PASSED", "SUCCESS")
                self.result_ready.emit("  FTP server is accessible", "INFO")
            else:
                self.result_ready.emit("📁 FTP Test: ❌ No FTP server", "INFO")
            
            # SMB results
            if results['smb']:
                smb_data = results['smb']
                self.result_ready.emit("🗂️  SMB Test: ✅ PASSED", "SUCCESS")
                self.result_ready.emit(f"  File sharing available on port {smb_data['port']}", "INFO")
            else:
                self.result_ready.emit("🗂️  SMB Test: ❌ No file sharing", "INFO")
            
            # Socket results
            if results['socket']:
                socket_data = results['socket']
                if socket_data['speed'] > best_speed:
                    best_speed = socket_data['speed']
                    best_method = "Socket Throughput"
                self.result_ready.emit("🔌 Socket Test: ✅ PASSED", "SUCCESS")
            else:
                self.result_ready.emit("🔌 Socket Test: ❌ Port not accessible", "WARNING")
            
            # Final assessment
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("📊 FINAL ASSESSMENT:", "SUCCESS")
            
            if best_speed > 0:
                self.result_ready.emit(f"  Best Speed Found: {best_speed:.1f} Mbps", "SUCCESS")
                self.result_ready.emit(f"  Best Method: {best_method}", "INFO")
                self.speed_update.emit(best_speed, "lan")
                
                if best_speed > 100:
                    self.result_ready.emit("  🚀 Excellent LAN performance!", "SUCCESS")
                elif best_speed > 10:
                    self.result_ready.emit("  ✅ Good LAN performance", "SUCCESS")
                else:
                    self.result_ready.emit("  ⚠️ Limited performance detected", "WARNING")
            else:
                self.result_ready.emit("  ❌ Could not measure LAN speed", "ERROR")
                self.result_ready.emit("  💡 Target may not have accessible services", "INFO")
            
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("💡 RECOMMENDATIONS:", "INFO")
            
            if not results['iperf']:
                self.result_ready.emit("  • Install iperf3 for accurate testing:", "INFO")
                self.result_ready.emit("    - Local: pip install iperf3", "INFO")
                self.result_ready.emit("    - Target: iperf3 -s (start server)", "INFO")
            
            if not any([results['http'], results['ftp'], results['smb']]):
                self.result_ready.emit("  • Consider enabling services on target:", "INFO")
                self.result_ready.emit("    - Web server (HTTP)", "INFO")
                self.result_ready.emit("    - File sharing (SMB/FTP)", "INFO")
            
        except Exception as e:
            self.result_ready.emit(f"Results compilation error: {str(e)}", "ERROR")
    
    def install_iperf3_helper(self):
        """Provide iperf3 installation guidance"""
        def _show_install_guide():
            try:
                self.result_ready.emit("📥 IPERF3 INSTALLATION GUIDE", "INFO")
                self.result_ready.emit("=" * 40, "INFO")
                
                system = platform.system().lower()
                
                if system == "windows":
                    self.result_ready.emit("🪟 Windows Installation:", "INFO")
                    self.result_ready.emit("1. Download from: https://iperf.fr/iperf-download.php", "INFO")
                    self.result_ready.emit("2. Or use: choco install iperf3", "INFO")
                    self.result_ready.emit("3. Or try: pip install iperf3", "INFO")
                elif system == "linux":
                    self.result_ready.emit("🐧 Linux Installation:", "INFO")
                    self.result_ready.emit("• Ubuntu/Debian: sudo apt install iperf3", "INFO")
                    self.result_ready.emit("• CentOS/RHEL: sudo yum install iperf3", "INFO")
                    self.result_ready.emit("• Fedora: sudo dnf install iperf3", "INFO")
                elif system == "darwin":
                    self.result_ready.emit("🍎 macOS Installation:", "INFO")
                    self.result_ready.emit("• Homebrew: brew install iperf3", "INFO")
                    self.result_ready.emit("• MacPorts: sudo port install iperf3", "INFO")
                
                self.result_ready.emit("", "INFO")
                self.result_ready.emit("🎯 USAGE:", "INFO")
                self.result_ready.emit("1. On target device: iperf3 -s", "INFO")
                self.result_ready.emit("2. In SigmaToolkit: Run LAN speed test", "INFO")
                self.result_ready.emit("3. Get accurate gigabit LAN speeds!", "INFO")
                
            except Exception as e:
                self.result_ready.emit(f"Install guide error: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_show_install_guide)
        thread.daemon = True
        thread.start()
    
    def stop_test(self):
        """Stop any running test"""
        self.test_running = False