# dns/dns_tools.py
import subprocess
import socket
import threading
import time
import re
from PyQt5.QtCore import QObject, pyqtSignal

class DNSTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def forward_lookup(self, domain):
        """Forward DNS lookup (domain to IP)"""
        def _forward_lookup():
            try:
                self.logger.debug(f"Starting forward DNS lookup for {domain}")
                self.result_ready.emit(f"Forward DNS lookup for {domain}...", "INFO")
                
                # Get IP address
                ip = socket.gethostbyname(domain)
                self.result_ready.emit(f"IP Address: {ip}", "SUCCESS")
                
                # Try to get all IP addresses
                try:
                    result = socket.getaddrinfo(domain, None)
                    ips = list(set([r[4][0] for r in result]))
                    if len(ips) > 1:
                        self.result_ready.emit(f"All IP addresses: {', '.join(ips)}", "INFO")
                except:
                    pass
                    
            except Exception as e:
                self.result_ready.emit(f"Forward DNS lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_forward_lookup)
        thread.daemon = True
        thread.start()
        
    def reverse_lookup(self, ip):
        """Reverse DNS lookup (IP to domain)"""
        def _reverse_lookup():
            try:
                self.logger.debug(f"Starting reverse DNS lookup for {ip}")
                self.result_ready.emit(f"Reverse DNS lookup for {ip}...", "INFO")
                
                # Validate IP format
                socket.inet_aton(ip)
                
                # Reverse lookup
                hostname = socket.gethostbyaddr(ip)
                self.result_ready.emit(f"Hostname: {hostname[0]}", "SUCCESS")
                
                if len(hostname[1]) > 0:
                    self.result_ready.emit(f"Aliases: {', '.join(hostname[1])}", "INFO")
                    
            except socket.error as e:
                self.result_ready.emit(f"Reverse DNS lookup error: {str(e)}", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Reverse DNS lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_reverse_lookup)
        thread.daemon = True
        thread.start()
        
    def mx_lookup(self, domain):
        """MX record lookup"""
        def _mx_lookup():
            try:
                self.logger.debug(f"Starting MX lookup for {domain}")
                self.result_ready.emit(f"MX record lookup for {domain}...", "INFO")
                
                # Use nslookup for MX records
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=MX", domain]
                else:
                    cmd = ["dig", "MX", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("MX Records:", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit("No MX records found or lookup failed", "WARNING")
                    if process.stderr:
                        self.result_ready.emit(process.stderr, "ERROR")
                        
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"MX lookup for {domain} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"MX lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_mx_lookup)
        thread.daemon = True
        thread.start()
        
    def txt_lookup(self, domain):
        """TXT record lookup (includes SPF)"""
        def _txt_lookup():
            try:
                self.logger.debug(f"Starting TXT lookup for {domain}")
                self.result_ready.emit(f"TXT record lookup for {domain}...", "INFO")
                
                # Use nslookup for TXT records
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=TXT", domain]
                else:
                    cmd = ["dig", "TXT", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("TXT Records:", "SUCCESS")
                    output = process.stdout
                    
                    # Parse and highlight SPF records
                    lines = output.split('\n')
                    for line in lines:
                        if 'v=spf1' in line.lower():
                            self.result_ready.emit(f"SPF Record: {line.strip()}", "SUCCESS")
                        elif line.strip():
                            self.result_ready.emit(line.strip(), "INFO")
                else:
                    self.result_ready.emit("No TXT records found or lookup failed", "WARNING")
                    if process.stderr:
                        self.result_ready.emit(process.stderr, "ERROR")
                        
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"TXT lookup for {domain} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"TXT lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_txt_lookup)
        thread.daemon = True
        thread.start()
        
    def ns_lookup(self, domain):
        """NS record lookup"""
        def _ns_lookup():
            try:
                self.logger.debug(f"Starting NS lookup for {domain}")
                self.result_ready.emit(f"NS record lookup for {domain}...", "INFO")
                
                # Use nslookup for NS records
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=NS", domain]
                else:
                    cmd = ["dig", "NS", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("Name Servers:", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit("No NS records found or lookup failed", "WARNING")
                    if process.stderr:
                        self.result_ready.emit(process.stderr, "ERROR")
                        
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"NS lookup for {domain} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"NS lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_ns_lookup)
        thread.daemon = True
        thread.start()
        
    def cname_lookup(self, domain):
        """CNAME record lookup"""
        def _cname_lookup():
            try:
                self.logger.debug(f"Starting CNAME lookup for {domain}")
                self.result_ready.emit(f"CNAME record lookup for {domain}...", "INFO")
                
                # Use nslookup for CNAME records
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=CNAME", domain]
                else:
                    cmd = ["dig", "CNAME", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("CNAME Records:", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit("No CNAME records found", "WARNING")
                    if process.stderr:
                        self.result_ready.emit(process.stderr, "ERROR")
                        
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"CNAME lookup for {domain} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"CNAME lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_cname_lookup)
        thread.daemon = True
        thread.start()
        
    def aaaa_lookup(self, domain):
        """AAAA record lookup (IPv6)"""
        def _aaaa_lookup():
            try:
                self.logger.debug(f"Starting AAAA lookup for {domain}")
                self.result_ready.emit(f"AAAA record lookup for {domain}...", "INFO")
                
                # Use nslookup for AAAA records
                import platform
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=AAAA", domain]
                else:
                    cmd = ["dig", "AAAA", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("IPv6 Addresses (AAAA):", "SUCCESS")
                    self.result_ready.emit(process.stdout, "INFO")
                else:
                    self.result_ready.emit("No AAAA records found", "WARNING")
                    if process.stderr:
                        self.result_ready.emit(process.stderr, "ERROR")
                        
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"AAAA lookup for {domain} timed out", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"AAAA lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_aaaa_lookup)
        thread.daemon = True
        thread.start()
        
    def all_records_lookup(self, domain):
        """Lookup all common DNS records"""
        def _all_records():
            self.result_ready.emit(f"=== Comprehensive DNS lookup for {domain} ===", "INFO")
            
            # Run all lookups with small delays
            self.forward_lookup(domain)
            time.sleep(1)
            self.mx_lookup(domain)
            time.sleep(1)
            self.txt_lookup(domain)
            time.sleep(1)
            self.ns_lookup(domain)
            time.sleep(1)
            self.cname_lookup(domain)
            time.sleep(1)
            self.aaaa_lookup(domain)
            
            self.result_ready.emit(f"=== DNS lookup completed for {domain} ===", "INFO")
                
        thread = threading.Thread(target=_all_records)
        thread.daemon = True
        thread.start()