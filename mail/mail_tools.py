# mail/mail_tools.py
import re
import threading
import time
import subprocess
import socket
from datetime import datetime
from email import message_from_string
from email.utils import parsedate_to_datetime, parseaddr
from PyQt5.QtCore import QObject, pyqtSignal

class MailTools(QObject):
    result_ready = pyqtSignal(str, str)  # result, level
    analysis_ready = pyqtSignal(dict, str)  # analysis_data, analysis_type
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def analyze_headers(self, headers_text):
        """Analyze email headers comprehensively"""
        def _analyze():
            try:
                self.logger.debug("Starting email header analysis")
                self.result_ready.emit("Analyzing email headers...", "INFO")
                
                # Parse headers using email library
                msg = message_from_string(headers_text)
                
                analysis_data = {
                    'headers': {},
                    'summary': '',
                    'analysis': '',
                    'delivery_path': {}
                }
                
                # Extract all headers
                for header, value in msg.items():
                    analysis_data['headers'][header] = value
                
                # Generate summary
                summary = self._generate_summary(msg)
                analysis_data['summary'] = summary
                
                # Generate detailed analysis
                detailed_analysis = self._generate_detailed_analysis(msg, headers_text)
                analysis_data['analysis'] = detailed_analysis
                
                # Analyze delivery path
                delivery_path = self._analyze_delivery_path(headers_text)
                analysis_data['delivery_path'] = delivery_path
                
                self.result_ready.emit("✅ Header analysis completed", "SUCCESS")
                self.analysis_ready.emit(analysis_data, "headers")
                
            except Exception as e:
                self.result_ready.emit(f"Header analysis error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_analyze)
        thread.daemon = True
        thread.start()
        
    def _generate_summary(self, msg):
        """Generate a quick summary of email headers"""
        summary_parts = []
        
        # Basic email info
        from_addr = msg.get('From', 'Unknown')
        to_addr = msg.get('To', 'Unknown')
        subject = msg.get('Subject', 'No Subject')
        date = msg.get('Date', 'Unknown')
        
        summary_parts.append(f"📧 Email Summary:")
        summary_parts.append(f"From: {from_addr}")
        summary_parts.append(f"To: {to_addr}")
        summary_parts.append(f"Subject: {subject}")
        summary_parts.append(f"Date: {date}")
        summary_parts.append("")
        
        # Authentication status
        auth_results = msg.get('Authentication-Results', '')
        if auth_results:
            spf_status = "UNKNOWN"
            dkim_status = "UNKNOWN"
            dmarc_status = "UNKNOWN"
            
            if 'spf=pass' in auth_results.lower():
                spf_status = "✅ PASS"
            elif 'spf=fail' in auth_results.lower():
                spf_status = "❌ FAIL"
            elif 'spf=softfail' in auth_results.lower():
                spf_status = "⚠️ SOFTFAIL"
            
            if 'dkim=pass' in auth_results.lower():
                dkim_status = "✅ PASS"
            elif 'dkim=fail' in auth_results.lower():
                dkim_status = "❌ FAIL"
            
            if 'dmarc=pass' in auth_results.lower():
                dmarc_status = "✅ PASS"
            elif 'dmarc=fail' in auth_results.lower():
                dmarc_status = "❌ FAIL"
            
            summary_parts.append(f"🔐 Authentication Status:")
            summary_parts.append(f"SPF: {spf_status}")
            summary_parts.append(f"DKIM: {dkim_status}")
            summary_parts.append(f"DMARC: {dmarc_status}")
            summary_parts.append("")
        
        # Count received headers (hops)
        received_headers = msg.get_all('Received') or []
        hop_count = len(received_headers)
        summary_parts.append(f"🛤️ Delivery Path: {hop_count} hops")
        
        # Check for suspicious indicators
        suspicious_indicators = []
        
        # Check for suspicious sender domains
        sender_name, sender_email = parseaddr(from_addr)
        if sender_email:
            sender_domain = sender_email.split('@')[-1] if '@' in sender_email else ''
            
            # Check for suspicious patterns
            if any(suspicious in sender_domain.lower() for suspicious in ['temp', 'disposable', 'guerrilla']):
                suspicious_indicators.append("Temporary/disposable sender domain")
        
        # Check for missing security headers
        if not msg.get('DKIM-Signature'):
            suspicious_indicators.append("Missing DKIM signature")
        
        if not auth_results:
            suspicious_indicators.append("Missing authentication results")
        
        # Check for unusual routing
        if hop_count > 10:
            suspicious_indicators.append(f"Unusual number of hops ({hop_count})")
        
        if suspicious_indicators:
            summary_parts.append(f"⚠️ Potential Issues:")
            for indicator in suspicious_indicators:
                summary_parts.append(f"  • {indicator}")
        else:
            summary_parts.append(f"✅ No obvious security issues detected")
        
        return "\n".join(summary_parts)
        
    def _generate_detailed_analysis(self, msg, headers_text):
        """Generate detailed header analysis"""
        analysis_parts = []
        
        analysis_parts.append("🔍 DETAILED HEADER ANALYSIS")
        analysis_parts.append("=" * 50)
        analysis_parts.append("")
        
        # Message ID analysis
        message_id = msg.get('Message-ID', '')
        if message_id:
            analysis_parts.append(f"📨 Message ID Analysis:")
            analysis_parts.append(f"  ID: {message_id}")
            
            # Extract domain from Message-ID
            id_match = re.search(r'@([^>]+)', message_id)
            if id_match:
                id_domain = id_match.group(1)
                analysis_parts.append(f"  Originating server: {id_domain}")
            analysis_parts.append("")
        
        # Return-Path analysis
        return_path = msg.get('Return-Path', '')
        if return_path:
            analysis_parts.append(f"↩️ Return Path Analysis:")
            analysis_parts.append(f"  Path: {return_path}")
            
            # Check if Return-Path matches From
            from_addr = msg.get('From', '')
            if return_path and from_addr:
                return_email = re.search(r'<([^>]+)>', return_path)
                from_email = re.search(r'<([^>]+)>', from_addr)
                
                if return_email and from_email:
                    if return_email.group(1) != from_email.group(1):
                        analysis_parts.append(f"  ⚠️ Return-Path differs from From address")
                    else:
                        analysis_parts.append(f"  ✅ Return-Path matches From address")
            analysis_parts.append("")
        
        # DKIM analysis
        dkim_signature = msg.get('DKIM-Signature', '')
        if dkim_signature:
            analysis_parts.append(f"🔑 DKIM Signature Analysis:")
            
            # Extract DKIM parameters
            dkim_params = {}
            for param in dkim_signature.split(';'):
                param = param.strip()
                if '=' in param:
                    key, value = param.split('=', 1)
                    dkim_params[key.strip()] = value.strip()
            
            if 'v' in dkim_params:
                analysis_parts.append(f"  Version: {dkim_params['v']}")
            if 'a' in dkim_params:
                analysis_parts.append(f"  Algorithm: {dkim_params['a']}")
            if 'd' in dkim_params:
                analysis_parts.append(f"  Domain: {dkim_params['d']}")
            if 's' in dkim_params:
                analysis_parts.append(f"  Selector: {dkim_params['s']}")
            
            analysis_parts.append("")
        
        # Received headers analysis
        received_headers = msg.get_all('Received') or []
        if received_headers:
            analysis_parts.append(f"🛤️ Delivery Path Analysis ({len(received_headers)} hops):")
            
            total_delay = 0
            prev_timestamp = None
            
            for i, received in enumerate(reversed(received_headers)):  # Start from oldest
                analysis_parts.append(f"  Hop {i+1}:")
                
                # Extract timestamp
                timestamp_match = re.search(r';(.+)$', received.replace('\n', ' '))
                if timestamp_match:
                    timestamp_str = timestamp_match.group(1).strip()
                    try:
                        timestamp = parsedate_to_datetime(timestamp_str)
                        analysis_parts.append(f"    Time: {timestamp}")
                        
                        if prev_timestamp:
                            delay = (timestamp - prev_timestamp).total_seconds()
                            total_delay += delay
                            if delay > 0:
                                analysis_parts.append(f"    Delay: {delay:.1f} seconds")
                        
                        prev_timestamp = timestamp
                    except:
                        analysis_parts.append(f"    Time: {timestamp_str} (parsing failed)")
                
                # Extract servers
                server_match = re.search(r'from\s+([^\s]+)', received)
                if server_match:
                    server = server_match.group(1)
                    analysis_parts.append(f"    Server: {server}")
                
                # Extract IP addresses
                ip_matches = re.findall(r'\[(\d+\.\d+\.\d+\.\d+)\]', received)
                for ip in ip_matches:
                    analysis_parts.append(f"    IP: {ip}")
                
                analysis_parts.append("")
            
            if total_delay > 0:
                analysis_parts.append(f"  📊 Total delivery time: {total_delay:.1f} seconds")
                if total_delay > 300:  # 5 minutes
                    analysis_parts.append(f"  ⚠️ Slow delivery detected")
                analysis_parts.append("")
        
        # Content-Type analysis
        content_type = msg.get('Content-Type', '')
        if content_type:
            analysis_parts.append(f"📄 Content Analysis:")
            analysis_parts.append(f"  Type: {content_type}")
            
            if 'multipart' in content_type.lower():
                analysis_parts.append(f"  📎 Multipart message (may contain attachments)")
            elif 'text/html' in content_type.lower():
                analysis_parts.append(f"  🌐 HTML message")
            elif 'text/plain' in content_type.lower():
                analysis_parts.append(f"  📝 Plain text message")
            
            analysis_parts.append("")
        
        # X-Headers analysis (additional headers)
        x_headers = []
        for header, value in msg.items():
            if header.lower().startswith('x-'):
                x_headers.append((header, value))
        
        if x_headers:
            analysis_parts.append(f"🔧 Extended Headers ({len(x_headers)} found):")
            for header, value in x_headers[:5]:  # Show first 5
                analysis_parts.append(f"  {header}: {value[:100]}{'...' if len(value) > 100 else ''}")
            if len(x_headers) > 5:
                analysis_parts.append(f"  ... and {len(x_headers) - 5} more")
            analysis_parts.append("")
        
        return "\n".join(analysis_parts)
        
    def _analyze_delivery_path(self, headers_text, options=None):
        """Analyze email delivery path"""
        if options is None:
            options = {
                'show_timestamps': True,
                'show_delays': True,
                'show_servers': True,
                'reverse_order': False
            }
        
        try:
            msg = message_from_string(headers_text)
            received_headers = msg.get_all('Received') or []
            
            path_parts = []
            stats_parts = []
            
            path_parts.append("🛤️ EMAIL DELIVERY PATH")
            path_parts.append("=" * 40)
            path_parts.append("")
            
            if not received_headers:
                path_parts.append("No Received headers found")
                return {'path': "\n".join(path_parts), 'stats': ''}
            
            timestamps = []
            servers = []
            total_delay = 0
            
            # Process headers in correct order
            headers_to_process = received_headers if options['reverse_order'] else list(reversed(received_headers))
            
            for i, received in enumerate(headers_to_process):
                hop_num = len(received_headers) - i if options['reverse_order'] else i + 1
                
                path_parts.append(f"📍 Hop {hop_num}:")
                
                # Extract server information
                if options['show_servers']:
                    server_match = re.search(r'from\s+([^\s]+)', received)
                    if server_match:
                        server = server_match.group(1)
                        servers.append(server)
                        path_parts.append(f"  🖥️  Server: {server}")
                    
                    # Extract IP addresses
                    ip_matches = re.findall(r'\[(\d+\.\d+\.\d+\.\d+)\]', received)
                    for ip in ip_matches:
                        path_parts.append(f"  🌐 IP: {ip}")
                
                # Extract and process timestamp
                if options['show_timestamps']:
                    timestamp_match = re.search(r';(.+)$', received.replace('\n', ' '))
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1).strip()
                        try:
                            timestamp = parsedate_to_datetime(timestamp_str)
                            timestamps.append(timestamp)
                            path_parts.append(f"  ⏰ Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                            
                            # Calculate delays
                            if options['show_delays'] and len(timestamps) > 1:
                                delay = (timestamps[-1] - timestamps[-2]).total_seconds()
                                total_delay += abs(delay)
                                if delay > 0:
                                    path_parts.append(f"  ⏱️  Delay: {delay:.1f} seconds")
                                elif delay < 0:
                                    path_parts.append(f"  ⚠️  Time regression: {abs(delay):.1f} seconds")
                                    
                        except Exception as e:
                            path_parts.append(f"  ⏰ Time: {timestamp_str} (parse error)")
                
                path_parts.append("")
            
            # Generate statistics
            stats_parts.append(f"📊 DELIVERY STATISTICS:")
            stats_parts.append(f"Total hops: {len(received_headers)}")
            
            if timestamps:
                stats_parts.append(f"Total delivery time: {total_delay:.1f} seconds")
                
                if total_delay < 10:
                    stats_parts.append("⚡ Very fast delivery")
                elif total_delay < 60:
                    stats_parts.append("✅ Normal delivery speed")
                elif total_delay < 300:
                    stats_parts.append("⏳ Moderate delivery delay")
                else:
                    stats_parts.append("🐌 Slow delivery detected")
            
            if servers:
                unique_servers = list(set(servers))
                stats_parts.append(f"Unique servers: {len(unique_servers)}")
                
                # Check for loops
                if len(servers) != len(unique_servers):
                    stats_parts.append("⚠️ Possible mail loops detected")
            
            return {
                'path': "\n".join(path_parts),
                'stats': "\n".join(stats_parts)
            }
            
        except Exception as e:
            return {
                'path': f"Error analyzing delivery path: {str(e)}",
                'stats': ''
            }
    
    def check_spf(self, domain, sender_ip=""):
        """Check SPF records for domain"""
        def _check_spf():
            try:
                self.logger.debug(f"Checking SPF for domain: {domain}")
                self.result_ready.emit(f"Checking SPF records for {domain}...", "INFO")
                
                # Query TXT records for SPF
                import subprocess
                import platform
                
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=TXT", domain]
                else:
                    cmd = ["dig", "TXT", domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                results = []
                spf_found = False
                
                if process.returncode == 0 and process.stdout.strip():
                    lines = process.stdout.strip().split('\n')
                    
                    for line in lines:
                        if 'v=spf1' in line.lower():
                            spf_found = True
                            results.append(f"✅ SPF Record Found:")
                            results.append(f"  {line.strip()}")
                            
                            # Parse SPF record
                            spf_analysis = self._analyze_spf_record(line, sender_ip)
                            results.extend(spf_analysis)
                            break
                    
                    if not spf_found:
                        results.append(f"❌ No SPF record found for {domain}")
                        results.append(f"💡 SPF helps prevent email spoofing")
                else:
                    results.append(f"❌ Could not query SPF records for {domain}")
                    if process.stderr:
                        results.append(f"Error: {process.stderr}")
                
                auth_data = {'results': '\n'.join(results)}
                self.analysis_ready.emit(auth_data, "authentication")
                self.result_ready.emit("SPF check completed", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"SPF check error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_check_spf)
        thread.daemon = True
        thread.start()
    
    def _analyze_spf_record(self, spf_record, sender_ip=""):
        """Analyze SPF record content"""
        analysis = []
        
        # Extract SPF mechanisms
        mechanisms = []
        if 'include:' in spf_record:
            includes = re.findall(r'include:([^\s]+)', spf_record)
            for include in includes:
                mechanisms.append(f"Include: {include}")
        
        if 'a:' in spf_record or ' a ' in spf_record:
            mechanisms.append("A record check enabled")
        
        if 'mx:' in spf_record or ' mx ' in spf_record:
            mechanisms.append("MX record check enabled")
        
        if 'ip4:' in spf_record:
            ip4s = re.findall(r'ip4:([^\s]+)', spf_record)
            for ip4 in ip4s:
                mechanisms.append(f"IPv4: {ip4}")
        
        if 'ip6:' in spf_record:
            ip6s = re.findall(r'ip6:([^\s]+)', spf_record)
            for ip6 in ip6s:
                mechanisms.append(f"IPv6: {ip6}")
        
        # Check policy
        if '~all' in spf_record:
            policy = "SoftFail (~all) - suspicious but not rejected"
        elif '-all' in spf_record:
            policy = "Fail (-all) - reject unauthorized senders"
        elif '+all' in spf_record:
            policy = "Pass (+all) - allow all senders (not recommended)"
        elif '?all' in spf_record:
            policy = "Neutral (?all) - no policy"
        else:
            policy = "Unknown policy"
        
        analysis.append(f"")
        analysis.append(f"📋 SPF Analysis:")
        if mechanisms:
            analysis.append(f"  Authorized mechanisms:")
            for mechanism in mechanisms:
                analysis.append(f"    • {mechanism}")
        
        analysis.append(f"  Policy: {policy}")
        
        # Test sender IP if provided
        if sender_ip:
            analysis.append(f"")
            analysis.append(f"🔍 Sender IP Test ({sender_ip}):")
            
            # Simple IP matching (basic implementation)
            ip_authorized = False
            
            # Check direct IP matches
            if f'ip4:{sender_ip}' in spf_record:
                ip_authorized = True
                analysis.append(f"  ✅ IP directly authorized")
            
            if not ip_authorized:
                analysis.append(f"  ⚠️ IP not explicitly authorized (may pass via include/mx/a)")
        
        return analysis
    
    def check_dkim(self, domain):
        """Check DKIM records for domain"""
        def _check_dkim():
            try:
                self.logger.debug(f"Checking DKIM for domain: {domain}")
                self.result_ready.emit(f"Checking DKIM records for {domain}...", "INFO")
                
                results = []
                
                # Common DKIM selectors to check
                selectors = ['default', 'google', 'k1', 'k2', 'mail', 'dkim', 'selector1', 'selector2']
                
                dkim_found = False
                
                for selector in selectors:
                    dkim_domain = f"{selector}._domainkey.{domain}"
                    
                    try:
                        import subprocess
                        import platform
                        
                        if platform.system().lower() == "windows":
                            cmd = ["nslookup", "-type=TXT", dkim_domain]
                        else:
                            cmd = ["dig", "TXT", dkim_domain, "+short"]
                        
                        process = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        
                        if process.returncode == 0 and process.stdout.strip():
                            lines = process.stdout.strip().split('\n')
                            for line in lines:
                                if 'v=DKIM1' in line or 'k=' in line or 'p=' in line:
                                    dkim_found = True
                                    results.append(f"✅ DKIM Record Found:")
                                    results.append(f"  Selector: {selector}")
                                    results.append(f"  Record: {line.strip()}")
                                    
                                    # Analyze DKIM record
                                    dkim_analysis = self._analyze_dkim_record(line)
                                    results.extend(dkim_analysis)
                                    results.append("")
                                    break
                    except:
                        continue
                
                if not dkim_found:
                    results.append(f"❌ No DKIM records found for {domain}")
                    results.append(f"💡 Checked selectors: {', '.join(selectors)}")
                    results.append(f"💡 DKIM provides email integrity and authenticity")
                
                auth_data = {'results': '\n'.join(results)}
                self.analysis_ready.emit(auth_data, "authentication")
                self.result_ready.emit("DKIM check completed", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"DKIM check error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_check_dkim)
        thread.daemon = True
        thread.start()
    
    def _analyze_dkim_record(self, dkim_record):
        """Analyze DKIM record content"""
        analysis = []
        
        # Parse DKIM parameters
        dkim_params = {}
        for param in dkim_record.split(';'):
            param = param.strip().replace('"', '')
            if '=' in param:
                key, value = param.split('=', 1)
                dkim_params[key.strip()] = value.strip()
        
        analysis.append(f"📋 DKIM Analysis:")
        
        if 'v' in dkim_params:
            analysis.append(f"  Version: {dkim_params['v']}")
        
        if 'k' in dkim_params:
            key_type = dkim_params['k']
            if key_type == 'rsa':
                analysis.append(f"  Key Type: RSA (standard)")
            else:
                analysis.append(f"  Key Type: {key_type}")
        
        if 'p' in dkim_params:
            public_key = dkim_params['p']
            if public_key:
                key_length = len(public_key)
                analysis.append(f"  Public Key: Present ({key_length} chars)")
                if key_length > 400:
                    analysis.append(f"    🔒 Strong key length")
                else:
                    analysis.append(f"    ⚠️ Shorter key length")
            else:
                analysis.append(f"  Public Key: Revoked (empty p= tag)")
        
        if 't' in dkim_params:
            flags = dkim_params['t']
            if 'y' in flags:
                analysis.append(f"  🧪 Test mode enabled")
            if 's' in flags:
                analysis.append(f"  🔒 Strict subdomain policy")
        
        return analysis
    
    def check_dmarc(self, domain):
        """Check DMARC records for domain"""
        def _check_dmarc():
            try:
                self.logger.debug(f"Checking DMARC for domain: {domain}")
                self.result_ready.emit(f"Checking DMARC records for {domain}...", "INFO")
                
                dmarc_domain = f"_dmarc.{domain}"
                
                import subprocess
                import platform
                
                if platform.system().lower() == "windows":
                    cmd = ["nslookup", "-type=TXT", dmarc_domain]
                else:
                    cmd = ["dig", "TXT", dmarc_domain, "+short"]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                results = []
                dmarc_found = False
                
                if process.returncode == 0 and process.stdout.strip():
                    lines = process.stdout.strip().split('\n')
                    
                    for line in lines:
                        if 'v=DMARC1' in line:
                            dmarc_found = True
                            results.append(f"✅ DMARC Record Found:")
                            results.append(f"  {line.strip()}")
                            
                            # Analyze DMARC record
                            dmarc_analysis = self._analyze_dmarc_record(line)
                            results.extend(dmarc_analysis)
                            break
                
                if not dmarc_found:
                    results.append(f"❌ No DMARC record found for {domain}")
                    results.append(f"💡 DMARC provides policy for handling auth failures")
                    results.append(f"💡 Helps prevent domain spoofing and phishing")
                
                auth_data = {'results': '\n'.join(results)}
                self.analysis_ready.emit(auth_data, "authentication")
                self.result_ready.emit("DMARC check completed", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"DMARC check error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_check_dmarc)
        thread.daemon = True
        thread.start()
    
    def _analyze_dmarc_record(self, dmarc_record):
        """Analyze DMARC record content"""
        analysis = []
        
        # Parse DMARC parameters
        dmarc_params = {}
        for param in dmarc_record.split(';'):
            param = param.strip().replace('"', '')
            if '=' in param:
                key, value = param.split('=', 1)
                dmarc_params[key.strip()] = value.strip()
        
        analysis.append(f"")
        analysis.append(f"📋 DMARC Analysis:")
        
        # Policy analysis
        if 'p' in dmarc_params:
            policy = dmarc_params['p']
            if policy == 'none':
                analysis.append(f"  Policy: Monitor only (p=none)")
                analysis.append(f"    📊 No action taken, monitoring phase")
            elif policy == 'quarantine':
                analysis.append(f"  Policy: Quarantine (p=quarantine)")
                analysis.append(f"    📥 Failed emails may go to spam")
            elif policy == 'reject':
                analysis.append(f"  Policy: Reject (p=reject)")
                analysis.append(f"    🚫 Failed emails are rejected")
        
        # Subdomain policy
        if 'sp' in dmarc_params:
            sp_policy = dmarc_params['sp']
            analysis.append(f"  Subdomain Policy: {sp_policy}")
        
        # Percentage
        if 'pct' in dmarc_params:
            percentage = dmarc_params['pct']
            analysis.append(f"  Enforcement: {percentage}% of messages")
            if int(percentage) < 100:
                analysis.append(f"    ⚠️ Partial enforcement enabled")
        
        # Reporting
        if 'rua' in dmarc_params:
            rua = dmarc_params['rua']
            analysis.append(f"  Aggregate Reports: {rua}")
        
        if 'ruf' in dmarc_params:
            ruf = dmarc_params['ruf']
            analysis.append(f"  Forensic Reports: {ruf}")
        
        # Alignment
        if 'adkim' in dmarc_params:
            adkim = dmarc_params['adkim']
            if adkim == 's':
                analysis.append(f"  DKIM Alignment: Strict")
            else:
                analysis.append(f"  DKIM Alignment: Relaxed")
        
        if 'aspf' in dmarc_params:
            aspf = dmarc_params['aspf']
            if aspf == 's':
                analysis.append(f"  SPF Alignment: Strict")
            else:
                analysis.append(f"  SPF Alignment: Relaxed")
        
        return analysis
    
    def comprehensive_auth_check(self, domain, sender_ip=""):
        """Run comprehensive authentication check"""
        def _comprehensive_check():
            try:
                self.result_ready.emit("=== COMPREHENSIVE EMAIL AUTHENTICATION ANALYSIS ===", "INFO")
                self.result_ready.emit(f"Domain: {domain}", "INFO")
                if sender_ip:
                    self.result_ready.emit(f"Sender IP: {sender_ip}", "INFO")
                self.result_ready.emit("", "INFO")
                
                # Run all checks in sequence
                self.result_ready.emit("1. Checking SPF records...", "INFO")
                time.sleep(0.5)
                self.check_spf(domain, sender_ip)
                
                time.sleep(3)
                
                self.result_ready.emit("2. Checking DKIM records...", "INFO")
                time.sleep(0.5)
                self.check_dkim(domain)
                
                time.sleep(3)
                
                self.result_ready.emit("3. Checking DMARC records...", "INFO")
                time.sleep(0.5)
                self.check_dmarc(domain)
                
                time.sleep(3)
                
                # Generate overall assessment
                self.result_ready.emit("4. Generating security assessment...", "INFO")
                time.sleep(1)
                
                overall_results = []
                overall_results.append("🔒 OVERALL SECURITY ASSESSMENT:")
                overall_results.append("=" * 40)
                overall_results.append("")
                
                # This is a simplified assessment - in a real implementation,
                # you'd collect the actual results from the individual checks
                overall_results.append("📊 Authentication Summary:")
                overall_results.append("  SPF: Check individual results above")
                overall_results.append("  DKIM: Check individual results above")
                overall_results.append("  DMARC: Check individual results above")
                overall_results.append("")
                
                overall_results.append("💡 Recommendations:")
                overall_results.append("  • Ensure all three protocols are implemented")
                overall_results.append("  • Use DMARC policy 'quarantine' or 'reject' for protection")
                overall_results.append("  • Monitor DMARC reports for authentication failures")
                overall_results.append("  • Keep DKIM keys updated and secure")
                overall_results.append("")
                
                auth_data = {'results': '\n'.join(overall_results)}
                self.analysis_ready.emit(auth_data, "authentication")
                
                self.result_ready.emit("=== COMPREHENSIVE CHECK COMPLETED ===", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"Comprehensive check error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_comprehensive_check)
        thread.daemon = True
        thread.start()
    
    def check_ip_reputation(self, ip_address):
        """Check IP reputation using multiple sources"""
        def _check_reputation():
            try:
                self.logger.debug(f"Checking reputation for IP: {ip_address}")
                self.result_ready.emit(f"Checking reputation for {ip_address}...", "INFO")
                
                results = []
                results.append(f"🔍 IP REPUTATION CHECK: {ip_address}")
                results.append("=" * 40)
                results.append("")
                
                # Basic IP validation
                try:
                    import ipaddress
                    ip_obj = ipaddress.ip_address(ip_address)
                    
                    if ip_obj.is_private:
                        results.append("📍 IP Type: Private/Internal")
                        results.append("⚠️ Private IPs are not in public blacklists")
                    elif ip_obj.is_loopback:
                        results.append("📍 IP Type: Loopback")
                    elif ip_obj.is_multicast:
                        results.append("📍 IP Type: Multicast")
                    else:
                        results.append("📍 IP Type: Public")
                        
                        # Check some basic reputation indicators
                        results.append("")
                        results.append("🛡️ Reputation Checks:")
                        
                        # Simple reverse DNS check
                        try:
                            import socket
                            hostname = socket.gethostbyaddr(ip_address)
                            results.append(f"  Reverse DNS: {hostname[0]}")
                            
                            # Check if hostname looks suspicious
                            suspicious_patterns = ['temp', 'dynamic', 'dhcp', 'pool', 'dial']
                            hostname_lower = hostname[0].lower()
                            
                            suspicious_found = any(pattern in hostname_lower for pattern in suspicious_patterns)
                            if suspicious_found:
                                results.append(f"  ⚠️ Hostname suggests dynamic/temporary IP")
                            else:
                                results.append(f"  ✅ Hostname appears stable")
                                
                        except socket.herror:
                            results.append(f"  Reverse DNS: Not found")
                            results.append(f"  ⚠️ No reverse DNS may indicate poor reputation")
                        
                        # Simple blacklist check simulation
                        # Note: In a real implementation, you'd query actual blacklist services
                        results.append("")
                        results.append("🚫 Blacklist Status:")
                        results.append("  💡 For real blacklist checking, use services like:")
                        results.append("    • Spamhaus Block List (SBL)")
                        results.append("    • Composite Blocking List (CBL)")
                        results.append("    • Exploits Block List (XBL)")
                        results.append("    • Policy Block List (PBL)")
                        results.append("")
                        results.append("  🔗 Check manually at:")
                        results.append(f"    • https://www.spamhaus.org/lookup/")
                        results.append(f"    • https://mxtoolbox.com/blacklists.aspx")
                        results.append(f"    • https://multirbl.valli.org/lookup/")
                        
                except ValueError:
                    results.append("❌ Invalid IP address format")
                
                results.append("")
                results.append("📊 Reputation Summary:")
                results.append("  Manual verification recommended for production use")
                results.append("  Consider using dedicated reputation services for automation")
                
                spam_data = {'results': '\n'.join(results)}
                self.analysis_ready.emit(spam_data, "spam")
                self.result_ready.emit("IP reputation check completed", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"IP reputation check error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_check_reputation)
        thread.daemon = True
        thread.start()
    
    def analyze_delivery_path(self, headers_text, options):
        """Analyze delivery path with custom options"""
        def _analyze_path():
            try:
                delivery_data = self._analyze_delivery_path(headers_text, options)
                self.analysis_ready.emit(delivery_data, "delivery_path")
                self.result_ready.emit("Delivery path analysis updated", "SUCCESS")
                
            except Exception as e:
                self.result_ready.emit(f"Delivery path analysis error: {str(e)}", "ERROR")
                
        thread = threading.Thread(target=_analyze_path)
        thread.daemon = True
        thread.start()