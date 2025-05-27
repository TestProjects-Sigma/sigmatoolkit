# speedtest/speedtest_tools.py - FIXED VERSION WITH SAFE LAN TESTING
import threading
import time
import socket
import subprocess
import json
import re
import os
import platform
from PyQt5.QtCore import QObject, pyqtSignal

class SpeedTestTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    progress_update = pyqtSignal(int, str)  # progress percentage, status
    speed_update = pyqtSignal(float, str)  # speed value, test type (download/upload)
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.test_running = False
        self.speedtest_cli_available = self.check_speedtest_cli()
        
    def check_speedtest_cli(self):
        """Check if speedtest CLI is available with better detection"""
        
        # First, try to detect what type of speedtest we have
        detected_cli = None
        
        # Test 1: Try official Ookla speedtest CLI
        try:
            result = subprocess.run(["speedtest", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Check if it's the official Ookla CLI by testing for specific arguments
                test_result = subprocess.run(["speedtest", "--help"], 
                                           capture_output=True, text=True, timeout=5)
                if "--accept-license" in test_result.stdout:
                    self.result_ready.emit("✅ Found official Speedtest CLI by Ookla", "SUCCESS")
                    self.result_ready.emit(f"Version: {result.stdout.strip()}", "INFO")
                    detected_cli = "speedtest"
                else:
                    # It's probably speedtest-cli aliased as speedtest
                    self.logger.debug("speedtest command found but appears to be speedtest-cli")
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Official speedtest CLI not found: {e}")
            
        # Test 2: Try speedtest-cli directly
        if not detected_cli:
            try:
                result = subprocess.run(["speedtest-cli", "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.result_ready.emit("✅ Found speedtest-cli (Python version)", "SUCCESS")
                    self.result_ready.emit(f"Version: {result.stdout.strip()}", "INFO")
                    detected_cli = "speedtest-cli"
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                self.logger.debug(f"speedtest-cli not found: {e}")
        
        if not detected_cli:
            self.result_ready.emit("❌ Speedtest CLI not found", "ERROR")
            self.result_ready.emit("💡 Install with: pip install speedtest-cli", "INFO")
            
        return detected_cli
        
    def speedtest_cli_test(self, server_id=None):
        """Run speedtest using the available CLI with better handling"""
        def _cli_test():
            try:
                self.test_running = True
                
                if not self.speedtest_cli_available:
                    self.result_ready.emit("❌ Speedtest CLI not available", "ERROR")
                    self.result_ready.emit("Please install speedtest CLI first", "WARNING")
                    return
                
                self.result_ready.emit("🚀 Running official Speedtest CLI test...", "INFO")
                self.result_ready.emit(f"Using: {self.speedtest_cli_available}", "INFO")
                
                # Build command based on available CLI
                if self.speedtest_cli_available == "speedtest":
                    # Official Ookla CLI
                    cmd = ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"]
                    if server_id:
                        cmd.extend(["--server-id", str(server_id)])
                elif self.speedtest_cli_available == "speedtest-cli":
                    # Python speedtest-cli
                    cmd = ["speedtest-cli", "--json"]
                    if server_id:
                        cmd.extend(["--server", str(server_id)])
                else:
                    self.result_ready.emit("❌ Unknown CLI type", "ERROR")
                    return
                
                self.logger.debug(f"Running command: {' '.join(cmd)}")
                
                # Show progress
                self.progress_update.emit(10, "Initializing speedtest...")
                
                # Start the test with better error handling
                try:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE, text=True)
                except FileNotFoundError:
                    self.result_ready.emit(f"❌ Command not found: {cmd[0]}", "ERROR")
                    return
                
                # Monitor progress with more realistic timing
                start_time = time.time()
                estimated_duration = 45
                
                while process.poll() is None and self.test_running:
                    elapsed = time.time() - start_time
                    progress = min(int((elapsed / estimated_duration) * 90), 90)
                    
                    if elapsed < 5:
                        status = "Finding best server..."
                    elif elapsed < 15:
                        status = "Testing latency and server selection..."
                    elif elapsed < 35:
                        status = "Testing download speed..."
                    elif elapsed < 45:
                        status = "Testing upload speed..."
                    else:
                        status = "Finalizing results..."
                    
                    self.progress_update.emit(progress, status)
                    time.sleep(1)
                
                if not self.test_running:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    self.result_ready.emit("⏹️ Speedtest cancelled by user", "WARNING")
                    return
                
                try:
                    stdout, stderr = process.communicate(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.result_ready.emit("⏱️ Speedtest process timed out", "ERROR")
                    return
                
                if process.returncode == 0 and stdout and stdout.strip():
                    self.result_ready.emit("✅ Speedtest completed successfully", "SUCCESS")
                    self.parse_speedtest_results(stdout)
                else:
                    self.result_ready.emit(f"❌ Speedtest failed (exit code: {process.returncode})", "ERROR")
                    if stderr:
                        self.result_ready.emit(f"Error details: {stderr}", "ERROR")
                    
            except Exception as e:
                self.result_ready.emit(f"❌ Speedtest error: {str(e)}", "ERROR")
                self.logger.debug(f"Speedtest exception: {e}")
            finally:
                self.test_running = False
                self.progress_update.emit(100, "Speedtest completed")
                
        thread = threading.Thread(target=_cli_test)
        thread.daemon = True
        thread.start()
        
    def parse_speedtest_results(self, json_output):
        """Parse speedtest CLI JSON output with better debugging"""
        try:
            # Clean the output - remove any non-JSON content
            json_output = json_output.strip()
            
            # Find JSON start and end
            json_start = json_output.find('{')
            json_end = json_output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.result_ready.emit("❌ No JSON data found in output", "ERROR")
                return
            
            clean_json = json_output[json_start:json_end]
            data = json.loads(clean_json)
            
            # Handle different CLI versions
            if "download" in data and "upload" in data:
                # Check if it's the official Ookla CLI format (newer)
                if isinstance(data.get("download"), dict) and "bandwidth" in data["download"]:
                    # Official Ookla CLI format
                    download_bps = data["download"]["bandwidth"]
                    upload_bps = data["upload"]["bandwidth"]
                    ping_ms = data["ping"]["latency"]
                    server_name = data["server"]["name"]
                    server_location = data["server"]["location"]
                    
                    # Convert from bytes/sec to Mbps
                    download_mbps = (download_bps * 8) / 1000000
                    upload_mbps = (upload_bps * 8) / 1000000
                    
                elif isinstance(data.get("download"), (int, float)):
                    # Python speedtest-cli format (older)
                    download_mbps = data["download"] / 1000000  # Convert from bps to Mbps
                    upload_mbps = data["upload"] / 1000000
                    ping_ms = data["ping"]
                    
                    # Server info for speedtest-cli
                    server_info = data.get("server", {})
                    server_name = server_info.get("sponsor", "Unknown")
                    server_country = server_info.get("country", "")
                    server_city = server_info.get("name", "")
                    server_location = f"{server_city}, {server_country}".strip(", ")
                    
                else:
                    self.result_ready.emit("❌ Unknown speedtest data format", "ERROR")
                    return
            else:
                self.result_ready.emit("❌ Missing download/upload data in results", "ERROR")
                return
            
            # Update real-time displays
            self.speed_update.emit(download_mbps, "download")
            self.speed_update.emit(upload_mbps, "upload")
            
            # Display results
            self.result_ready.emit("🎯 Official Speedtest Results:", "SUCCESS")
            self.result_ready.emit(f"📍 Server: {server_name} ({server_location})", "INFO")
            self.result_ready.emit(f"⬇️  Download: {download_mbps:.1f} Mbps", "SUCCESS")
            self.result_ready.emit(f"⬆️  Upload: {upload_mbps:.1f} Mbps", "SUCCESS")
            self.result_ready.emit(f"📡 Latency: {ping_ms:.1f} ms", "INFO")
            
            # Performance assessment
            if download_mbps > 700:
                assessment = "🚀 Excellent gigabit performance!"
                level = "SUCCESS"
            elif download_mbps > 500:
                assessment = "✅ Good high-speed performance"
                level = "SUCCESS"
            elif download_mbps > 100:
                assessment = "⚡ Decent broadband speed"
                level = "INFO"
            else:
                assessment = "⚠️ Below expected for high-speed connection"
                level = "WARNING"
            
            self.result_ready.emit(f"📊 Assessment: {assessment}", level)
            
        except json.JSONDecodeError as e:
            self.result_ready.emit(f"❌ JSON parsing error: {str(e)}", "ERROR")
        except Exception as e:
            self.result_ready.emit(f"❌ Error parsing speedtest results: {str(e)}", "ERROR")
            
    def list_speedtest_servers(self):
        """List available speedtest servers"""
        def _list_servers():
            try:
                self.result_ready.emit("🔍 Finding available speedtest servers...", "INFO")
                
                if self.speedtest_cli_available == "speedtest":
                    cmd = ["speedtest", "--servers", "--format=json"]
                elif self.speedtest_cli_available == "speedtest-cli":
                    cmd = ["speedtest-cli", "--list"]
                else:
                    self.result_ready.emit("Speedtest CLI not available", "ERROR")
                    return
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    if self.speedtest_cli_available == "speedtest":
                        # Parse JSON format
                        try:
                            data = json.loads(result.stdout)
                            servers = data.get("servers", [])
                            
                            self.result_ready.emit(f"📋 Found {len(servers)} speedtest servers:", "SUCCESS")
                            
                            # Show top 10 closest servers
                            for i, server in enumerate(servers[:10]):
                                name = server.get("name", "Unknown")
                                location = server.get("location", "Unknown")
                                distance = server.get("distance", 0)
                                server_id = server.get("id", "")
                                
                                self.result_ready.emit(
                                    f"  {i+1}. {name} ({location}) - {distance:.1f} km - ID: {server_id}", 
                                    "INFO"
                                )
                                
                        except json.JSONDecodeError:
                            self.result_ready.emit("Could not parse server list", "ERROR")
                    else:
                        # Parse text format from speedtest-cli
                        lines = result.stdout.split('\n')
                        server_count = 0
                        
                        for line in lines:
                            if ') ' in line and server_count < 10:
                                self.result_ready.emit(f"  {line.strip()}", "INFO")
                                server_count += 1
                                
                        self.result_ready.emit(f"📋 Showing first 10 of available servers", "SUCCESS")
                else:
                    self.result_ready.emit(f"Error listing servers: {result.stderr}", "ERROR")
                    
            except Exception as e:
                self.result_ready.emit(f"Error listing servers: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_list_servers)
        thread.daemon = True
        thread.start()
        
    def ping_latency_test(self, host, count=10):
        """Test latency with ping"""
        def _ping_test():
            try:
                self.logger.debug(f"Starting latency test to {host}")
                self.result_ready.emit(f"Testing latency to {host}...", "INFO")
                
                if platform.system().lower() == "windows":
                    cmd = ["ping", "-n", str(count), host]
                else:
                    cmd = ["ping", "-c", str(count), host]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if process.returncode == 0:
                    output = process.stdout
                    latencies = []
                    
                    lines = output.split('\n')
                    for line in lines:
                        if 'time=' in line:
                            try:
                                time_part = line.split('time=')[1].split()[0]
                                if 'ms' in time_part:
                                    latency = float(time_part.replace('ms', ''))
                                    latencies.append(latency)
                            except:
                                pass
                    
                    if latencies:
                        avg_latency = sum(latencies) / len(latencies)
                        min_latency = min(latencies)
                        max_latency = max(latencies)
                        
                        self.result_ready.emit(f"✅ Latency Test Results for {host}:", "SUCCESS")
                        self.result_ready.emit(f"  Average: {avg_latency:.1f} ms", "INFO")
                        self.result_ready.emit(f"  Minimum: {min_latency:.1f} ms", "INFO")
                        self.result_ready.emit(f"  Maximum: {max_latency:.1f} ms", "INFO")
                        
                        self.speed_update.emit(avg_latency, "latency")
                        
                        if avg_latency < 20:
                            quality = "Excellent"
                        elif avg_latency < 50:
                            quality = "Good"  
                        elif avg_latency < 100:
                            quality = "Fair"
                        else:
                            quality = "Poor"
                        
                        self.result_ready.emit(f"  Quality: {quality}", "SUCCESS" if quality in ["Excellent", "Good"] else "WARNING")
                    else:
                        self.result_ready.emit("Could not parse latency data", "WARNING")
                else:
                    self.result_ready.emit(f"Ping test failed: {process.stderr}", "ERROR")
                    
            except Exception as e:
                self.result_ready.emit(f"Latency test error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_ping_test)
        thread.daemon = True
        thread.start()
        
    def lan_speed_test(self, target_ip, port=12345):
        """Safe LAN speed test with proper error handling"""
        def _lan_test():
            try:
                self.logger.debug(f"Starting LAN speed test to {target_ip}:{port}")
                self.result_ready.emit(f"🏠 Testing LAN speed to {target_ip}:{port}...", "INFO")
                
                # Validate IP address first
                try:
                    import ipaddress
                    ip_obj = ipaddress.ip_address(target_ip)
                    self.result_ready.emit(f"✅ Valid IP address: {target_ip}", "INFO")
                except ValueError:
                    self.result_ready.emit(f"❌ Invalid IP address: {target_ip}", "ERROR")
                    return
                
                # Test basic connectivity first
                self.progress_update.emit(10, "Testing connectivity...")
                
                # Simple ping test first
                try:
                    if platform.system().lower() == "windows":
                        ping_cmd = ["ping", "-n", "1", target_ip]
                    else:
                        ping_cmd = ["ping", "-c", "1", target_ip]
                    
                    ping_result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=5)
                    
                    if ping_result.returncode == 0:
                        self.result_ready.emit(f"✅ {target_ip} is reachable", "SUCCESS")
                    else:
                        self.result_ready.emit(f"⚠️ {target_ip} may not be reachable", "WARNING")
                        self.result_ready.emit("Continuing with LAN test anyway...", "INFO")
                        
                except Exception as e:
                    self.result_ready.emit(f"Ping test failed: {str(e)}", "WARNING")
                
                self.progress_update.emit(30, "Testing port connectivity...")
                
                # Test port connectivity
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    result = sock.connect_ex((target_ip, port))
                    sock.close()
                    
                    if result == 0:
                        self.result_ready.emit(f"✅ Port {port} is open on {target_ip}", "SUCCESS")
                        self.progress_update.emit(50, "Port is accessible, testing speed...")
                        
                        # Simple speed estimation based on latency
                        self._estimate_lan_speed(target_ip, port)
                        
                    else:
                        self.result_ready.emit(f"❌ Port {port} is closed on {target_ip}", "ERROR")
                        self.result_ready.emit("💡 LAN speed test requires a service listening on the target port", "INFO")
                        self.result_ready.emit("💡 Try common ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 445 (SMB)", "INFO")
                        
                        # Still provide some basic network info
                        self._provide_basic_lan_info(target_ip)
                        
                except socket.error as e:
                    self.result_ready.emit(f"❌ Connection error: {str(e)}", "ERROR")
                    self._provide_basic_lan_info(target_ip)
                    
                except Exception as e:
                    self.result_ready.emit(f"❌ LAN test error: {str(e)}", "ERROR")
                    
            except Exception as e:
                self.result_ready.emit(f"❌ LAN speed test failed: {str(e)}", "ERROR")
                self.logger.error(f"LAN test exception: {e}")
            finally:
                self.progress_update.emit(100, "LAN test completed")
                
        thread = threading.Thread(target=_lan_test)
        thread.daemon = True
        thread.start()
    
    def _estimate_lan_speed(self, target_ip, port):
        """Estimate LAN speed based on latency and basic tests"""
        try:
            # Simple latency-based estimation
            start_time = time.time()
            
            # Multiple quick connections to estimate speed
            connection_times = []
            
            for i in range(5):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    
                    connect_start = time.time()
                    result = sock.connect_ex((target_ip, port))
                    connect_time = (time.time() - connect_start) * 1000  # Convert to ms
                    
                    sock.close()
                    
                    if result == 0:
                        connection_times.append(connect_time)
                        self.progress_update.emit(50 + (i * 10), f"Testing connection {i+1}/5...")
                    
                    time.sleep(0.1)  # Small delay between tests
                    
                except Exception:
                    pass
            
            if connection_times:
                avg_latency = sum(connection_times) / len(connection_times)
                
                # Estimate speed based on latency (rough approximation)
                if avg_latency < 1:
                    estimated_speed = 1000  # Very fast LAN
                elif avg_latency < 5:
                    estimated_speed = 100   # Fast LAN
                elif avg_latency < 20:
                    estimated_speed = 10    # Standard LAN
                else:
                    estimated_speed = 1     # Slow connection
                
                self.speed_update.emit(estimated_speed, "lan")
                
                self.result_ready.emit("🏠 LAN Speed Test Results:", "SUCCESS")
                self.result_ready.emit(f"  Average Latency: {avg_latency:.2f} ms", "INFO")
                self.result_ready.emit(f"  Estimated Speed: ~{estimated_speed} Mbps", "INFO")
                
                if avg_latency < 1:
                    self.result_ready.emit("  Quality: ⚡ Excellent LAN performance", "SUCCESS")
                elif avg_latency < 5:
                    self.result_ready.emit("  Quality: ✅ Good LAN performance", "SUCCESS")
                elif avg_latency < 20:
                    self.result_ready.emit("  Quality: ⚠️ Average LAN performance", "WARNING")
                else:
                    self.result_ready.emit("  Quality: 🐌 Slow LAN connection", "WARNING")
                
                self.result_ready.emit("", "INFO")
                self.result_ready.emit("💡 Note: This is a basic estimation", "INFO")
                self.result_ready.emit("💡 For accurate LAN testing, use dedicated tools like iperf3", "INFO")
                
            else:
                self.result_ready.emit("❌ Could not establish reliable connections for speed testing", "ERROR")
                
        except Exception as e:
            self.result_ready.emit(f"Speed estimation error: {str(e)}", "ERROR")
    
    def _provide_basic_lan_info(self, target_ip):
        """Provide basic LAN information when speed test fails"""
        try:
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("🏠 Basic LAN Information:", "INFO")
            self.result_ready.emit(f"  Target: {target_ip}", "INFO")
            
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(target_ip)
                self.result_ready.emit(f"  Hostname: {hostname[0]}", "INFO")
            except:
                self.result_ready.emit(f"  Hostname: Not available", "INFO")
            
            # Network class info
            try:
                import ipaddress
                ip_obj = ipaddress.ip_address(target_ip)
                
                if ip_obj.is_private:
                    if target_ip.startswith('192.168.'):
                        network_type = "Home/Small Office Network (Class C)"
                    elif target_ip.startswith('10.'):
                        network_type = "Large Private Network (Class A)"
                    elif target_ip.startswith('172.'):
                        network_type = "Medium Private Network (Class B)"
                    else:
                        network_type = "Private Network"
                else:
                    network_type = "Public Network"
                
                self.result_ready.emit(f"  Network Type: {network_type}", "INFO")
                
            except:
                pass
            
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("💡 For LAN speed testing:", "INFO")
            self.result_ready.emit("  • Ensure target has a service running (HTTP, SSH, SMB)", "INFO")
            self.result_ready.emit("  • Try ports: 22, 80, 443, 445, 21, 23", "INFO")
            self.result_ready.emit("  • Use dedicated tools like iperf3 for accurate testing", "INFO")
            
        except Exception as e:
            self.result_ready.emit(f"Basic info error: {str(e)}", "ERROR")
        
    def comprehensive_speed_test(self, server_info):
        """Run comprehensive speed test with CLI if available"""
        def _comprehensive_test():
            if self.speedtest_cli_available:
                self.result_ready.emit("=== OFFICIAL SPEEDTEST.NET TEST ===", "INFO")
                self.result_ready.emit("Using official CLI for maximum accuracy", "INFO")
                time.sleep(1)
                
                # Run official speedtest
                self.speedtest_cli_test()
            else:
                self.result_ready.emit("=== BUILT-IN SPEED TEST ===", "INFO")
                self.result_ready.emit("Install speedtest CLI for better accuracy", "WARNING")
                
                host = server_info.get("host", "google.com")
                
                # Basic latency test
                self.result_ready.emit("\n1. Testing latency...", "INFO")
                time.sleep(0.5)
                self.ping_latency_test(host, 10)
                
                time.sleep(3)
                self.result_ready.emit("\n⚠️ For accurate gigabit speeds, install speedtest CLI!", "WARNING")
                
        thread = threading.Thread(target=_comprehensive_test)
        thread.daemon = True
        thread.start()
        
    def stop_test(self):
        """Stop any running test"""
        self.test_running = False
        self.result_ready.emit("Speed test stopped by user", "WARNING")