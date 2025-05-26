# speedtest/speedtest_tools.py - WITH SPEEDTEST.NET CLI INTEGRATION
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
        
        # Test servers for fallback
        self.test_servers = [
            {"name": "Speedtest.net CLI", "url": "speedtest-cli", "host": "speedtest.net"},
            {"name": "Cloudflare CDN", "url": "https://speed.cloudflare.com", "host": "speed.cloudflare.com"},
            {"name": "Fast.com (Netflix)", "url": "https://fast.com", "host": "fast.com"},
            {"name": "Google", "url": "https://www.google.com", "host": "www.google.com"},
            {"name": "Microsoft Azure", "url": "https://download.microsoft.com", "host": "download.microsoft.com"}
        ]
        
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
        
        # Test 3: Check if 'speedtest' is actually speedtest-cli
        if not detected_cli:
            try:
                result = subprocess.run(["speedtest", "--help"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and "--json" in result.stdout and "--simple" in result.stdout:
                    # This looks like speedtest-cli, not official Ookla
                    self.result_ready.emit("✅ Found speedtest-cli (aliased as 'speedtest')", "SUCCESS")
                    detected_cli = "speedtest-as-cli"  # Special case
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                self.logger.debug(f"speedtest help check failed: {e}")
        
        if not detected_cli:
            # Neither found - provide installation guidance
            self.result_ready.emit("❌ Speedtest CLI not found", "ERROR")
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("📥 To install Speedtest CLI:", "INFO")
            self.result_ready.emit("", "INFO")
            
            import platform
            system = platform.system().lower()
            
            if system == "windows":
                self.result_ready.emit("🪟 Windows Options:", "INFO")
                self.result_ready.emit("1. pip install speedtest-cli", "INFO")
                self.result_ready.emit("2. Download from: https://www.speedtest.net/apps/cli", "INFO")
                self.result_ready.emit("3. choco install speedtest", "INFO")
            elif system == "linux":
                self.result_ready.emit("🐧 Linux Options:", "INFO")
                self.result_ready.emit("1. sudo apt install speedtest-cli", "INFO")
                self.result_ready.emit("2. pip install speedtest-cli", "INFO")
            elif system == "darwin":
                self.result_ready.emit("🍎 macOS Options:", "INFO")
                self.result_ready.emit("1. brew install speedtest-cli", "INFO")
                self.result_ready.emit("2. pip install speedtest-cli", "INFO")
            
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("⚠️ Using built-in tests for now (less accurate for gigabit)", "WARNING")
            
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
                elif self.speedtest_cli_available == "speedtest-as-cli":
                    # speedtest command that's actually speedtest-cli
                    cmd = ["speedtest", "--json"]
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
                    self.result_ready.emit("Please check your installation and PATH", "WARNING")
                    
                    # Suggest fallback
                    if self.speedtest_cli_available == "speedtest":
                        self.result_ready.emit("💡 Try installing: pip install speedtest-cli", "INFO")
                    return
                
                # Monitor progress with more realistic timing
                start_time = time.time()
                estimated_duration = 45  # speedtest-cli usually takes longer
                
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
                
                self.logger.debug(f"Process return code: {process.returncode}")
                self.logger.debug(f"stdout length: {len(stdout) if stdout else 0}")
                self.logger.debug(f"stderr: {stderr}")
                
                if process.returncode == 0:
                    if stdout and stdout.strip():
                        self.result_ready.emit("✅ Speedtest completed successfully", "SUCCESS")
                        self.parse_speedtest_results(stdout)
                    else:
                        self.result_ready.emit("❌ Speedtest returned empty results", "ERROR")
                        self.result_ready.emit(f"Command used: {' '.join(cmd)}", "INFO")
                        if stderr:
                            self.result_ready.emit(f"Error output: {stderr}", "ERROR")
                        self.result_ready.emit("💡 Try the '🔧 Test CLI' button to verify your setup", "INFO")
                else:
                    self.result_ready.emit(f"❌ Speedtest failed (exit code: {process.returncode})", "ERROR")
                    if stderr:
                        self.result_ready.emit(f"Error details: {stderr}", "ERROR")
                        
                        # Provide specific help based on error
                        if "not found" in stderr.lower():
                            self.result_ready.emit("💡 CLI not found in PATH", "INFO")
                        elif "license" in stderr.lower():
                            self.result_ready.emit("💡 Try running the command manually first to accept license", "INFO")
                        elif "network" in stderr.lower():
                            self.result_ready.emit("💡 Check your internet connection", "INFO")
                    
                    self.result_ready.emit("💡 The '🔧 Test CLI' button works, so try that instead", "WARNING")
                    
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
            self.logger.debug(f"Raw JSON output length: {len(json_output)}")
            self.logger.debug(f"First 200 chars: {json_output[:200]}")
            
            # Clean the output - remove any non-JSON content
            json_output = json_output.strip()
            
            # Find JSON start and end
            json_start = json_output.find('{')
            json_end = json_output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.result_ready.emit("❌ No JSON data found in output", "ERROR")
                self.result_ready.emit(f"Raw output: {json_output[:500]}", "INFO")
                return
            
            clean_json = json_output[json_start:json_end]
            self.logger.debug(f"Cleaned JSON: {clean_json[:200]}...")
            
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
                    
                    self.logger.debug(f"Ookla format: D={download_mbps:.1f} U={upload_mbps:.1f}")
                    
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
                    
                    self.logger.debug(f"Python CLI format: D={download_mbps:.1f} U={upload_mbps:.1f}")
                else:
                    self.result_ready.emit("❌ Unknown speedtest data format", "ERROR")
                    self.result_ready.emit(f"Download field type: {type(data.get('download'))}", "INFO")
                    self.result_ready.emit(f"Sample data: {str(data)[:300]}", "INFO")
                    return
            else:
                self.result_ready.emit("❌ Missing download/upload data in results", "ERROR")
                self.result_ready.emit(f"Available keys: {list(data.keys())}", "INFO")
                return
            
            # Update real-time displays
            self.speed_update.emit(download_mbps, "download")
            self.speed_update.emit(upload_mbps, "upload")
            self.speed_update.emit(ping_ms, "latency")
            
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
            
            # Additional info
            if "client" in data:
                client_info = data["client"]
                if "isp" in client_info:
                    self.result_ready.emit(f"🌐 ISP: {client_info['isp']}", "INFO")
                if "ip" in client_info:
                    self.result_ready.emit(f"🔗 IP: {client_info['ip']}", "INFO")
            
            self.result_ready.emit("✨ These are your REAL internet speeds!", "SUCCESS")
            
        except json.JSONDecodeError as e:
            self.result_ready.emit(f"❌ JSON parsing error: {str(e)}", "ERROR")
            self.result_ready.emit("Raw output (first 500 chars):", "INFO")
            self.result_ready.emit(json_output[:500], "INFO")
            self.result_ready.emit("", "INFO")
            self.result_ready.emit("💡 Debugging tips:", "INFO")
            self.result_ready.emit("1. Try running 'speedtest-cli --json' manually", "INFO")
            self.result_ready.emit("2. Check if speedtest-cli is the latest version", "INFO")
            self.result_ready.emit("3. Try 'pip install --upgrade speedtest-cli'", "INFO")
        except Exception as e:
            self.result_ready.emit(f"❌ Error parsing speedtest results: {str(e)}", "ERROR")
            self.result_ready.emit(f"Data type: {type(json_output)}", "INFO")
            self.result_ready.emit(f"Data length: {len(json_output) if json_output else 0}", "INFO")
            
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
                        
                        if len(latencies) > 1:
                            variance = sum((x - avg_latency) ** 2 for x in latencies) / len(latencies)
                            jitter = variance ** 0.5
                        else:
                            jitter = 0
                        
                        self.result_ready.emit(f"✅ Latency Test Results for {host}:", "SUCCESS")
                        self.result_ready.emit(f"  Average: {avg_latency:.1f} ms", "INFO")
                        self.result_ready.emit(f"  Minimum: {min_latency:.1f} ms", "INFO")
                        self.result_ready.emit(f"  Maximum: {max_latency:.1f} ms", "INFO")
                        self.result_ready.emit(f"  Jitter: {jitter:.1f} ms", "INFO")
                        
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