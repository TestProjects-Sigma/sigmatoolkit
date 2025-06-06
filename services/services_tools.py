# services/services_tools.py
import threading
import time
import socket
import subprocess
import requests
import json
from datetime import datetime
from urllib.parse import urlparse
from PyQt5.QtCore import QObject, pyqtSignal

class ServicesTools(QObject):
    service_checked = pyqtSignal(str, str, float, str)  # name, status, response_time, details
    batch_complete = pyqtSignal()
    result_ready = pyqtSignal(str, str)  # message, level
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.services = {}
        self.last_check_results = {}
        
    def add_service(self, name, url, check_type="http", category="Custom"):
        """Add a service to monitoring"""
        service_id = f"{category}_{name}".replace(" ", "_")
        
        self.services[service_id] = {
            "name": name,
            "url": url,
            "type": check_type,
            "category": category,
            "enabled": True,
            "timeout": 10,
            "added_time": datetime.now().isoformat()
        }
        
        self.logger.debug(f"Added service: {name} ({url}) - Type: {check_type}")
        
    def remove_service(self, name):
        """Remove a service from monitoring"""
        service_to_remove = None
        for service_id, service in self.services.items():
            if service["name"] == name:
                service_to_remove = service_id
                break
                
        if service_to_remove:
            del self.services[service_to_remove]
            if service_to_remove in self.last_check_results:
                del self.last_check_results[service_to_remove]
            self.logger.debug(f"Removed service: {name}")
            
    def get_services_by_category(self):
        """Get services organized by category"""
        categories = {}
        
        for service_id, service in self.services.items():
            category = service["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(service)
            
        return categories
        
    def get_status_summary(self):
        """Get summary of service statuses"""
        summary = {
            "total": len(self.services),
            "healthy": 0,
            "warning": 0,
            "critical": 0
        }
        
        for service_id, result in self.last_check_results.items():
            if result["status"] == "healthy":
                summary["healthy"] += 1
            elif result["status"] == "warning":
                summary["warning"] += 1
            else:
                summary["critical"] += 1
                
        return summary
        
    def check_all_services(self):
        """Check all services"""
        def _check_all():
            self.logger.debug("Starting batch service check")
            
            for service_id, service in self.services.items():
                if service["enabled"]:
                    self._check_single_service(service)
                    time.sleep(0.5)  # Small delay between checks
                    
            self.batch_complete.emit()
            self.result_ready.emit("✅ All services checked", "SUCCESS")
            
        thread = threading.Thread(target=_check_all)
        thread.daemon = True
        thread.start()
        
    def test_single_service(self, name, url, check_type):
        """Test a single service configuration"""
        def _test_service():
            test_service = {
                "name": name,
                "url": url,
                "type": check_type,
                "timeout": 10
            }
            
            self._check_single_service(test_service)
            
        thread = threading.Thread(target=_test_service)
        thread.daemon = True
        thread.start()
        
    def _check_single_service(self, service):
        """Check a single service and emit results"""
        start_time = time.time()
        status = "critical"
        details = ""
        response_time = 0
        
        try:
            if service["type"] == "http":
                status, response_time, details = self._check_http(service["url"], service["timeout"])
            elif service["type"] == "ping":
                status, response_time, details = self._check_ping(service["url"], service["timeout"])
            elif service["type"] == "port":
                status, response_time, details = self._check_port(service["url"], service["timeout"])
            elif service["type"] == "dns":
                status, response_time, details = self._check_dns(service["url"], service["timeout"])
            elif service["type"] == "api":
                status, response_time, details = self._check_api(service["url"], service["timeout"])
                
        except Exception as e:
            status = "critical"
            details = f"Check failed: {str(e)}"
            response_time = 0
            self.logger.error(f"Service check error for {service['name']}: {e}")
            
        # Store result - FIXED: Properly close the f-string
        service_key = f"{service.get('category', 'Custom')}_{service['name']}".replace(" ", "_")
        
        self.last_check_results[service_key] = {
            "status": status,
            "response_time": response_time,
            "details": details,
            "last_checked": datetime.now().isoformat()
        }
        
        # Emit result
        self.service_checked.emit(service["name"], status, response_time, details)
        
    def _check_http(self, url, timeout):
        """Check HTTP/HTTPS service"""
        try:
            self.logger.debug(f"Checking HTTP: {url}")
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            start_time = time.time()
            response = requests.get(url, timeout=timeout, verify=False, 
                                  headers={'User-Agent': 'SigmaToolkit-ServiceMonitor/1.0'})
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = "healthy"
                details = f"HTTP {response.status_code} - OK"
            elif 200 <= response.status_code < 400:
                status = "warning"
                details = f"HTTP {response.status_code} - Redirect/Info"
            else:
                status = "critical"
                details = f"HTTP {response.status_code} - Error"
                
            return status, response_time, details
            
        except requests.exceptions.Timeout:
            return "critical", 0, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return "critical", 0, "Connection failed"
        except requests.exceptions.SSLError:
            return "warning", 0, "SSL certificate issue"
        except Exception as e:
            return "critical", 0, f"HTTP check failed: {str(e)}"
            
    def _check_ping(self, host, timeout):
        """Check ping connectivity"""
        try:
            self.logger.debug(f"Checking ping: {host}")
            
            # Remove protocol if present
            if '://' in host:
                host = urlparse(host).netloc or urlparse(host).path
                
            import platform
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), host]
                
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                # Try to extract actual ping time from output
                output = result.stdout
                if 'time=' in output:
                    try:
                        time_part = output.split('time=')[1].split()[0]
                        if 'ms' in time_part:
                            ping_time = float(time_part.replace('ms', ''))
                            response_time = ping_time
                    except:
                        pass
                        
                if response_time < 100:
                    status = "healthy"
                elif response_time < 500:
                    status = "warning"
                else:
                    status = "critical"
                    
                details = f"Ping successful - {response_time:.1f}ms"
            else:
                status = "critical"
                details = "Ping failed - Host unreachable"
                response_time = 0
                
            return status, response_time, details
            
        except subprocess.TimeoutExpired:
            return "critical", 0, "Ping timeout"
        except Exception as e:
            return "critical", 0, f"Ping check failed: {str(e)}"
            
    def _check_port(self, target, timeout):
        """Check port connectivity"""
        try:
            self.logger.debug(f"Checking port: {target}")
            
            # Parse host:port or URL
            if '://' in target:
                parsed = urlparse(target)
                host = parsed.netloc.split(':')[0]
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            elif ':' in target:
                host, port = target.split(':')
                port = int(port)
            else:
                host = target
                port = 80  # Default port
                
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000
            sock.close()
            
            if result == 0:
                status = "healthy"
                details = f"Port {port} open on {host}"
            else:
                status = "critical"
                details = f"Port {port} closed on {host}"
                response_time = 0
                
            return status, response_time, details
            
        except socket.timeout:
            return "critical", 0, "Port check timeout"
        except Exception as e:
            return "critical", 0, f"Port check failed: {str(e)}"
            
    def _check_dns(self, domain, timeout):
        """Check DNS resolution"""
        try:
            self.logger.debug(f"Checking DNS: {domain}")
            
            # Remove protocol if present
            if '://' in domain:
                domain = urlparse(domain).netloc or urlparse(domain).path
                
            start_time = time.time()
            ip = socket.gethostbyname(domain)
            response_time = (time.time() - start_time) * 1000
            
            status = "healthy"
            details = f"DNS resolved to {ip}"
            
            return status, response_time, details
            
        except socket.gaierror:
            return "critical", 0, "DNS resolution failed"
        except Exception as e:
            return "critical", 0, f"DNS check failed: {str(e)}"
            
    def _check_api(self, url, timeout):
        """Check API endpoint with custom logic"""
        try:
            self.logger.debug(f"Checking API: {url}")
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            start_time = time.time()
            response = requests.get(url, timeout=timeout, verify=False,
                                  headers={'User-Agent': 'SigmaToolkit-ServiceMonitor/1.0'})
            response_time = (time.time() - start_time) * 1000
            
            # Custom API logic - check for specific response patterns
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for common health check patterns
                if any(keyword in content for keyword in ['ok', 'healthy', 'success', 'up']):
                    status = "healthy"
                    details = f"API healthy - {response.status_code}"
                elif any(keyword in content for keyword in ['error', 'fail', 'down']):
                    status = "critical"
                    details = f"API reports errors - {response.status_code}"
                else:
                    status = "warning"
                    details = f"API responding but status unclear - {response.status_code}"
            else:
                status = "critical"
                details = f"API error - HTTP {response.status_code}"
                
            return status, response_time, details
            
        except requests.exceptions.Timeout:
            return "critical", 0, "API timeout"
        except requests.exceptions.ConnectionError:
            return "critical", 0, "API connection failed"
        except Exception as e:
            return "critical", 0, f"API check failed: {str(e)}"
            
    def export_status_report(self, filepath):
        """Export current status to a report file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("SigmaToolkit Service Status Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                summary = self.get_status_summary()
                f.write("SUMMARY:\n")
                f.write(f"Total Services: {summary['total']}\n")
                f.write(f"Healthy: {summary['healthy']}\n")
                f.write(f"Warning: {summary['warning']}\n")
                f.write(f"Critical: {summary['critical']}\n\n")
                
                categories = self.get_services_by_category()
                
                for category, services in categories.items():
                    f.write(f"\n{category.upper()}:\n")
                    f.write("-" * len(category) + "\n")
                    
                    for service in services:
                        service_key = f"{category}_{service['name']}".replace(" ", "_")
                        result = self.last_check_results.get(service_key, {})
                        
                        status = result.get('status', 'unknown').upper()
                        response_time = result.get('response_time', 0)
                        last_checked = result.get('last_checked', 'Never')
                        
                        f.write(f"  {service['name']}: {status}")
                        if response_time > 0:
                            f.write(f" ({response_time:.0f}ms)")
                        f.write(f" - {service['url']}\n")
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False
            
    def get_microsoft365_official_status(self):
        """Get Microsoft 365 official service status (if available)"""
        def _get_m365_status():
            try:
                # This would require Microsoft Graph API access
                # For now, we'll check the public status page
                url = "https://admin.microsoft.com/Adminportal/Home"
                
                status, response_time, details = self._check_http(url, 10)
                
                self.result_ready.emit(
                    f"Microsoft 365 Admin Portal: {details}", 
                    "SUCCESS" if status == "healthy" else "WARNING"
                )
                
                # Note: For full M365 status, you'd want to integrate with:
                # - Microsoft Graph Service Communications API
                # - Azure Service Health API
                # This requires authentication and proper API setup
                
            except Exception as e:
                self.result_ready.emit(f"M365 status check failed: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_get_m365_status)
        thread.daemon = True
        thread.start()
        
    def load_services_from_config(self, config_path):
        """Load services from a configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for service_config in config.get('services', []):
                self.add_service(
                    service_config['name'],
                    service_config['url'],
                    service_config.get('type', 'http'),
                    service_config.get('category', 'Custom')
                )
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return False
            
    def save_services_to_config(self, config_path):
        """Save current services to a configuration file"""
        try:
            config = {
                "services": [
                    {
                        "name": service["name"],
                        "url": service["url"],
                        "type": service["type"],
                        "category": service["category"]
                    }
                    for service in self.services.values()
                ],
                "export_time": datetime.now().isoformat()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False