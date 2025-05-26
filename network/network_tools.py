# network/network_tools.py
import subprocess
import socket
import threading
import time
import re
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def ping(self, host, count=4):
        """Ping a host"""
        def _ping():
            try:
                self.logger.debug(f"Starting ping to {host} with {count} packets")
                self.result_ready.emit(f"Pinging {host}...", "INFO")
                
                # Build ping command based on OS
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["ping", "-n", str(count), host]
                else:
                    cmd = ["ping", "-c", str(count), host]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if process.returncode == 0:
                    self.result_ready.emit(f"Ping to {host} successful:", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit(f"Ping to {host} failed:", "ERROR")
                    self.result_ready.emit(process.stderr, "ERROR")
                    
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"Ping to {host} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Ping error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_ping)
        thread.daemon = True
        thread.start()
        
    def traceroute(self, host):
        """Traceroute to a host"""
        def _traceroute():
            try:
                self.logger.debug(f"Starting traceroute to {host}")
                self.result_ready.emit(f"Tracing route to {host}...", "INFO")
                
                # Build traceroute command based on OS
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["tracert", host]
                else:
                    cmd = ["traceroute", host]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if process.returncode == 0:
                    self.result_ready.emit(f"Traceroute to {host} completed:", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit(f"Traceroute to {host} failed:", "ERROR")
                    self.result_ready.emit(process.stderr, "ERROR")
                    
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"Traceroute to {host} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Traceroute error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_traceroute)
        thread.daemon = True
        thread.start()
        
    def port_scan(self, host, ports):
        """Scan ports on a host"""
        def _port_scan():
            try:
                self.logger.debug(f"Starting port scan on {host} for ports {ports}")
                self.result_ready.emit(f"Scanning ports on {host}...", "INFO")
                
                # Parse port range
                if '-' in ports:
                    start, end = map(int, ports.split('-'))
                    port_list = range(start, end + 1)
                else:
                    port_list = [int(p.strip()) for p in ports.split(',')]
                
                open_ports = []
                closed_ports = []
                
                for port in port_list:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    
                    try:
                        result = sock.connect_ex((host, port))
                        if result == 0:
                            open_ports.append(port)
                            self.result_ready.emit(f"Port {port}: OPEN", "SUCCESS")
                        else:
                            closed_ports.append(port)
                            self.logger.debug(f"Port {port}: CLOSED")
                    except Exception as e:
                        self.logger.debug(f"Port {port}: Error - {str(e)}")
                    finally:
                        sock.close()
                
                # Summary
                self.result_ready.emit(f"\nPort scan completed for {host}", "INFO")
                self.result_ready.emit(f"Open ports: {open_ports if open_ports else 'None'}", "INFO")
                self.result_ready.emit(f"Total ports scanned: {len(port_list)}", "INFO")
                
            except Exception as e:
                self.result_ready.emit(f"Port scan error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_port_scan)
        thread.daemon = True
        thread.start()
        
    def dns_lookup(self, host):
        """Perform DNS lookup"""
        def _dns_lookup():
            try:
                self.logger.debug(f"Starting DNS lookup for {host}")
                self.result_ready.emit(f"DNS lookup for {host}...", "INFO")
                
                # Get IP address
                ip = socket.gethostbyname(host)
                self.result_ready.emit(f"IP Address: {ip}", "SUCCESS")
                
                # Reverse lookup
                try:
                    reverse = socket.gethostbyaddr(ip)
                    self.result_ready.emit(f"Reverse DNS: {reverse[0]}", "INFO")
                except:
                    self.result_ready.emit("Reverse DNS: Not available", "WARNING")
                    
            except Exception as e:
                self.result_ready.emit(f"DNS lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_dns_lookup)
        thread.daemon = True
        thread.start()

# network/__init__.py
# Empty file to make it a package