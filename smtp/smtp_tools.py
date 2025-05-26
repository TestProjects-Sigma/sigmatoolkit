# smtp/smtp_tools.py
import smtplib
import socket
import ssl
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtCore import QObject, pyqtSignal

class SMTPTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def test_connection(self, server, port, use_tls=False, use_ssl=False, timeout=10):
        """Test SMTP server connection"""
        def _test_connection():
            try:
                self.logger.debug(f"Testing connection to {server}:{port}")
                self.result_ready.emit(f"Testing connection to {server}:{port}...", "INFO")
                
                if use_ssl:
                    # Direct SSL connection (port 465 typically)
                    self.result_ready.emit("Using SSL/TLS encryption", "INFO")
                    server_obj = smtplib.SMTP_SSL(server, port, timeout=timeout)
                else:
                    # Standard connection
                    server_obj = smtplib.SMTP(server, port, timeout=timeout)
                    
                    if use_tls:
                        # STARTTLS (port 587 typically)
                        self.result_ready.emit("Starting TLS encryption...", "INFO")
                        server_obj.starttls()
                        self.result_ready.emit("TLS encryption enabled", "SUCCESS")
                
                # Get server greeting
                response = server_obj.noop()
                self.result_ready.emit(f"Server response: {response}", "INFO")
                
                # Get server capabilities
                try:
                    capabilities = server_obj.esmtp_features
                    if capabilities:
                        self.result_ready.emit("Server capabilities:", "INFO")
                        for feature, params in capabilities.items():
                            if params:
                                self.result_ready.emit(f"  {feature}: {' '.join(params)}", "INFO")
                            else:
                                self.result_ready.emit(f"  {feature}", "INFO")
                except:
                    pass
                
                server_obj.quit()
                self.result_ready.emit(f"✅ Connection to {server}:{port} successful!", "SUCCESS")
                
            except smtplib.SMTPConnectError as e:
                self.result_ready.emit(f"Connection failed: {str(e)}", "ERROR")
            except smtplib.SMTPServerDisconnected as e:
                self.result_ready.emit(f"Server disconnected: {str(e)}", "ERROR")
            except socket.timeout:
                self.result_ready.emit(f"Connection timed out after {timeout}s", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Connection error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_test_connection)
        thread.daemon = True
        thread.start()
        
    def test_authentication(self, server, port, username, password, use_tls=False, use_ssl=False, timeout=10):
        """Test SMTP authentication"""
        def _test_auth():
            try:
                self.logger.debug(f"Testing authentication for {username} on {server}:{port}")
                self.result_ready.emit(f"Testing authentication for {username}...", "INFO")
                
                if use_ssl:
                    server_obj = smtplib.SMTP_SSL(server, port, timeout=timeout)
                else:
                    server_obj = smtplib.SMTP(server, port, timeout=timeout)
                    if use_tls:
                        server_obj.starttls()
                
                # Test login
                server_obj.login(username, password)
                self.result_ready.emit(f"✅ Authentication successful for {username}", "SUCCESS")
                
                # Get auth methods supported
                try:
                    if hasattr(server_obj, 'esmtp_features') and 'auth' in server_obj.esmtp_features:
                        auth_methods = server_obj.esmtp_features['auth']
                        self.result_ready.emit(f"Supported auth methods: {' '.join(auth_methods)}", "INFO")
                except:
                    pass
                
                server_obj.quit()
                
            except smtplib.SMTPAuthenticationError as e:
                self.result_ready.emit(f"❌ Authentication failed: {str(e)}", "ERROR")
            except smtplib.SMTPConnectError as e:
                self.result_ready.emit(f"Connection failed: {str(e)}", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Authentication error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_test_auth)
        thread.daemon = True
        thread.start()
        
    def send_test_email(self, server, port, username, password, from_email, to_email, 
                       subject="SigmaToolkit Test Email", use_tls=False, use_ssl=False, timeout=10):
        """Send a test email"""
        def _send_test():
            try:
                self.logger.debug(f"Sending test email from {from_email} to {to_email}")
                self.result_ready.emit(f"Sending test email to {to_email}...", "INFO")
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject
                
                # Email body
                body = f"""This is a test email sent from SigmaToolkit SMTP Tester.

Server: {server}:{port}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
Encryption: {'SSL' if use_ssl else 'TLS' if use_tls else 'None'}

If you received this email, your SMTP configuration is working correctly!

---
SigmaToolkit - Sigma's IT Swiss Army Knife
"""
                msg.attach(MIMEText(body, 'plain'))
                
                # Connect and send
                if use_ssl:
                    server_obj = smtplib.SMTP_SSL(server, port, timeout=timeout)
                else:
                    server_obj = smtplib.SMTP(server, port, timeout=timeout)
                    if use_tls:
                        server_obj.starttls()
                
                if username and password:
                    server_obj.login(username, password)
                    self.result_ready.emit("Authenticated successfully", "SUCCESS")
                
                # Send email
                text = msg.as_string()
                server_obj.sendmail(from_email, to_email, text)
                server_obj.quit()
                
                self.result_ready.emit(f"✅ Test email sent successfully to {to_email}!", "SUCCESS")
                self.result_ready.emit("Check the recipient's inbox and spam folder", "INFO")
                
            except smtplib.SMTPAuthenticationError as e:
                self.result_ready.emit(f"Authentication failed: {str(e)}", "ERROR")
            except smtplib.SMTPRecipientsRefused as e:
                self.result_ready.emit(f"Recipient refused: {str(e)}", "ERROR")
            except smtplib.SMTPSenderRefused as e:
                self.result_ready.emit(f"Sender refused: {str(e)}", "ERROR")
            except smtplib.SMTPDataError as e:
                self.result_ready.emit(f"SMTP data error: {str(e)}", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"Email sending error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_send_test)
        thread.daemon = True
        thread.start()
        
    def check_mx_records(self, domain):
        """Check MX records for a domain"""
        def _check_mx():
            try:
                self.logger.debug(f"Checking MX records for {domain}")
                self.result_ready.emit(f"Checking MX records for {domain}...", "INFO")
                
                import subprocess
                import platform
                
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=MX", domain]
                else:
                    cmd = ["dig", "MX", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    self.result_ready.emit("MX Records found:", "SUCCESS")
                    
                    # Parse and sort MX records by priority
                    mx_records = []
                    lines = process.stdout.strip().split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line and ('mail exchanger' in line.lower() or 
                                   (not platform.system().lower() == "windows" and line)):
                            mx_records.append(line)
                    
                    for record in mx_records:
                        self.result_ready.emit(f"  {record}", "INFO")
                        
                    if mx_records:
                        self.result_ready.emit("✅ Domain has mail servers configured", "SUCCESS")
                else:
                    self.result_ready.emit(f"❌ No MX records found for {domain}", "WARNING")
                    self.result_ready.emit("This domain cannot receive email", "WARNING")
                    
            except subprocess.TimeoutExpired:
                self.result_ready.emit(f"MX lookup timed out for {domain}", "ERROR")
            except Exception as e:
                self.result_ready.emit(f"MX lookup error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_check_mx)
        thread.daemon = True
        thread.start()
        
    def test_port_connectivity(self, server, ports=[25, 465, 587, 2525]):
        """Test connectivity to common SMTP ports"""
        def _test_ports():
            try:
                self.logger.debug(f"Testing SMTP port connectivity to {server}")
                self.result_ready.emit(f"Testing SMTP ports on {server}...", "INFO")
                
                open_ports = []
                closed_ports = []
                
                for port in ports:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    try:
                        result = sock.connect_ex((server, port))
                        if result == 0:
                            open_ports.append(port)
                            # Get port description
                            port_desc = {
                                25: "SMTP (Plain)",
                                465: "SMTPS (SSL)",
                                587: "SMTP (TLS/STARTTLS)",
                                2525: "SMTP (Alternative)"
                            }
                            desc = port_desc.get(port, "SMTP")
                            self.result_ready.emit(f"✅ Port {port}: OPEN ({desc})", "SUCCESS")
                        else:
                            closed_ports.append(port)
                            self.logger.debug(f"Port {port}: CLOSED")
                    except Exception as e:
                        closed_ports.append(port)
                        self.logger.debug(f"Port {port}: Error - {str(e)}")
                    finally:
                        sock.close()
                
                # Summary
                self.result_ready.emit(f"\nPort scan summary for {server}:", "INFO")
                if open_ports:
                    self.result_ready.emit(f"Open SMTP ports: {open_ports}", "SUCCESS")
                else:
                    self.result_ready.emit("No SMTP ports found open", "WARNING")
                
                if closed_ports:
                    self.result_ready.emit(f"Closed ports: {closed_ports}", "INFO")
                
            except Exception as e:
                self.result_ready.emit(f"Port connectivity test error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_test_ports)
        thread.daemon = True
        thread.start()
        
    def comprehensive_smtp_test(self, server, port, username="", password="", 
                               from_email="", to_email="", use_tls=False, use_ssl=False):
        """Run a comprehensive SMTP test"""
        def _comprehensive_test():
            self.result_ready.emit("=== Comprehensive SMTP Test Started ===", "INFO")
            self.result_ready.emit(f"Target: {server}:{port}", "INFO")
            
            # Test 1: Port connectivity
            self.result_ready.emit("\n1. Testing port connectivity...", "INFO")
            time.sleep(0.5)
            self.test_port_connectivity(server, [port])
            
            time.sleep(2)
            
            # Test 2: Basic connection
            self.result_ready.emit("\n2. Testing SMTP connection...", "INFO")
            time.sleep(0.5)
            self.test_connection(server, port, use_tls, use_ssl)
            
            time.sleep(3)
            
            # Test 3: Authentication (if credentials provided)
            if username and password:
                self.result_ready.emit("\n3. Testing authentication...", "INFO")
                time.sleep(0.5)
                self.test_authentication(server, port, username, password, use_tls, use_ssl)
                time.sleep(3)
            else:
                self.result_ready.emit("\n3. Skipping authentication test (no credentials)", "WARNING")
            
            # Test 4: Send test email (if all details provided)
            if username and password and from_email and to_email:
                self.result_ready.emit("\n4. Sending test email...", "INFO")
                time.sleep(0.5)
                self.send_test_email(server, port, username, password, from_email, to_email,
                                   "SigmaToolkit Comprehensive SMTP Test", use_tls, use_ssl)
            else:
                self.result_ready.emit("\n4. Skipping email test (incomplete details)", "WARNING")
            
            time.sleep(2)
            self.result_ready.emit("\n=== Comprehensive SMTP Test Completed ===", "INFO")
                
        thread = threading.Thread(target=_comprehensive_test)
        thread.daemon = True
        thread.start()