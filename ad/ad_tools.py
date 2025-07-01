# ad/ad_tools.py
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta
import ssl
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from ldap3 import Server, Connection, ALL, NTLM, Tls
    from ldap3.core.exceptions import LDAPException
    LDAP3_AVAILABLE = True
except ImportError:
    LDAP3_AVAILABLE = False

# Enable MD4 for NTLM if available (required for newer Python versions)
try:
    import hashlib
    hashlib.new('md4')
except ValueError:
    try:
        from Crypto.Hash import MD4
        def _md4_new(data=b''):
            h = MD4.new()
            if data:
                h.update(data)
            return h
        hashlib.md4 = _md4_new
        hashlib.new('md4', b'test')
    except (ImportError, Exception):
        pass

class ADConnectionTestWorker(QThread):
    """Worker thread for testing AD connection"""
    
    success = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        """Test the connection"""
        if not LDAP3_AVAILABLE:
            self.error.emit("LDAP3 library not available. Please install: pip install ldap3")
            return
            
        try:
            # Setup TLS configuration for secure connection
            tls_config = None
            if self.params['use_ssl']:
                tls_config = Tls(
                    validate=ssl.CERT_NONE,
                    version=ssl.PROTOCOL_TLS,
                    ciphers='HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA'
                )
            
            # Create server connection
            server = Server(
                self.params['server'],
                port=self.params['port'],
                use_ssl=self.params['use_ssl'],
                tls=tls_config,
                get_info=ALL
            )
            
            # Try different authentication methods
            auth_methods = [
                ("NTLM", lambda: Connection(server, user=f"{self.params['domain']}\\{self.params['username']}", 
                                          password=self.params['password'], authentication=NTLM)),
                ("Simple", lambda: Connection(server, user=f"{self.params['username']}@{self.params['domain']}", 
                                            password=self.params['password'], authentication='SIMPLE')),
                ("Simple DN", lambda: Connection(server, user=f"cn={self.params['username']},{self.params['base_dn']}", 
                                               password=self.params['password'], authentication='SIMPLE'))
            ]
            
            last_error = None
            for auth_name, conn_func in auth_methods:
                try:
                    conn = conn_func()
                    if conn.bind():
                        # Test a simple search to verify permissions
                        conn.search(
                            search_base=self.params['base_dn'],
                            search_filter="(objectClass=*)",
                            search_scope='BASE',
                            attributes=['objectClass']
                        )
                        
                        conn.unbind()
                        self.success.emit(f"Connected successfully using {auth_name} authentication.")
                        return
                    else:
                        last_error = f"{auth_name}: Bind failed - {conn.result}"
                except Exception as e:
                    last_error = f"{auth_name}: {str(e)}"
                    if conn:
                        try:
                            conn.unbind()
                        except:
                            pass
            
            # If we get here, all methods failed
            self.error.emit(f"All authentication methods failed. Last error: {last_error}")
            
        except Exception as e:
            self.error.emit(f"Connection test failed: {str(e)}")


class ADPasswordWorker(QThread):
    """Worker thread for Active Directory password operations"""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        self._is_running = True
        
    def stop(self):
        """Stop the worker thread"""
        self._is_running = False
        
    def run(self):
        """Main worker thread execution"""
        if not LDAP3_AVAILABLE:
            self.error.emit("LDAP3 library not available. Please install: pip install ldap3")
            return
            
        try:
            self.progress.emit(10)
            
            # Setup TLS configuration for secure connection
            tls_config = None
            if self.params['use_ssl']:
                tls_config = Tls(
                    validate=ssl.CERT_NONE,
                    version=ssl.PROTOCOL_TLS,
                    ciphers='HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA'
                )
            
            # Create server connection
            server = Server(
                self.params['server'],
                port=self.params['port'],
                use_ssl=self.params['use_ssl'],
                tls=tls_config,
                get_info=ALL
            )
            
            self.progress.emit(30)
            
            # Try different authentication methods
            conn = None
            auth_methods = [
                ("NTLM", lambda: Connection(server, user=f"{self.params['domain']}\\{self.params['username']}", 
                                          password=self.params['password'], authentication=NTLM)),
                ("Simple", lambda: Connection(server, user=f"{self.params['username']}@{self.params['domain']}", 
                                            password=self.params['password'], authentication='SIMPLE'))
            ]
            
            connected = False
            for auth_name, conn_func in auth_methods:
                try:
                    conn = conn_func()
                    if conn.bind():
                        connected = True
                        break
                except Exception as e:
                    if "MD4" in str(e):
                        try:
                            conn = Connection(
                                server, 
                                user=f"{self.params['username']}@{self.params['domain']}", 
                                password=self.params['password'], 
                                authentication='SIMPLE'
                            )
                            if conn.bind():
                                connected = True
                                break
                        except:
                            pass
                    continue
            
            if not connected:
                raise Exception("Failed to authenticate with any method. Check credentials and server settings.")
            
            self.progress.emit(50)
            
            if not self._is_running:
                return
            
            # Search for users with password information
            search_filter = "(&(objectClass=user)(objectCategory=person))"
            attributes = [
                'sAMAccountName', 'displayName', 'mail',
                'pwdLastSet', 'userAccountControl'
            ]
            
            conn.search(
                search_base=self.params['base_dn'],
                search_filter=search_filter,
                attributes=attributes
            )
            
            self.progress.emit(70)
            
            users_info = []
            total_entries = len(conn.entries)
            
            for i, entry in enumerate(conn.entries):
                if not self._is_running:
                    break
                
                try:
                    user_info = self._process_user_entry(entry)
                    if user_info:
                        users_info.append(user_info)
                except Exception as e:
                    print(f"Error processing user {entry.sAMAccountName}: {e}")
                
                # Update progress
                progress = 70 + int((i / total_entries) * 25)
                self.progress.emit(progress)
            
            conn.unbind()
            self.progress.emit(100)
            self.finished.emit(users_info)
            
        except LDAPException as e:
            self.error.emit(f"LDAP Error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Connection Error: {str(e)}")
    
    def _process_user_entry(self, entry):
        """Process individual user entry to extract password information"""
        try:
            username = str(entry.sAMAccountName.value) if entry.sAMAccountName else "unknown"
            display_name = str(entry.displayName.value) if entry.displayName and entry.displayName.value else username
            email = str(entry.mail.value) if entry.mail and entry.mail.value else ""
            
            # Get password last set time
            if not entry.pwdLastSet or not entry.pwdLastSet.value:
                return None
            
            # Check if pwdLastSet is already a datetime or needs conversion
            pwd_last_set_raw = entry.pwdLastSet.value
            
            if isinstance(pwd_last_set_raw, datetime):
                pwd_last_set_dt = pwd_last_set_raw
                if pwd_last_set_dt.tzinfo:
                    pwd_last_set_dt = pwd_last_set_dt.replace(tzinfo=None)
            elif isinstance(pwd_last_set_raw, int):
                if pwd_last_set_raw == 0:
                    return None
                pwd_last_set_dt = datetime(1601, 1, 1) + timedelta(microseconds=pwd_last_set_raw/10)
            else:
                return None
            
            # Get user account control flags
            uac = 0
            if entry.userAccountControl and entry.userAccountControl.value:
                try:
                    uac = int(entry.userAccountControl.value)
                except (ValueError, TypeError):
                    uac = 0
            
            account_disabled = bool(uac & 0x2)  # ACCOUNTDISABLE flag
            password_never_expires = bool(uac & 0x10000)  # DONT_EXPIRE_PASSWD flag
            
            # Calculate password expiration
            if password_never_expires:
                password_expires = datetime.max
                days_until_expiry = 999999
            else:
                # Use standard 90-day password policy
                max_age_days = 90
                password_expires = pwd_last_set_dt + timedelta(days=max_age_days)
                days_until_expiry = (password_expires - datetime.now()).days
            
            return {
                'username': username,
                'display_name': display_name,
                'email': email,
                'password_last_set': pwd_last_set_dt,
                'password_expires': password_expires,
                'days_until_expiry': days_until_expiry,
                'account_disabled': account_disabled,
                'password_never_expires': password_never_expires
            }
            
        except Exception as e:
            print(f"Error processing user {username if 'username' in locals() else 'unknown'}: {e}")
            return None


class ADPasswordTools:
    """Tools for Active Directory password operations"""
    
    def __init__(self, logger):
        self.logger = logger
        
    def test_connection_async(self, params, success_callback, error_callback):
        """Test AD connection asynchronously"""
        worker = ADConnectionTestWorker(params)
        worker.success.connect(success_callback)
        worker.error.connect(error_callback)
        worker.start()
        return worker
        
    def get_password_data_async(self, params, success_callback, error_callback, progress_callback):
        """Get password data asynchronously"""
        worker = ADPasswordWorker(params)
        worker.finished.connect(success_callback)
        worker.error.connect(error_callback)
        worker.progress.connect(progress_callback)
        worker.start()
        return worker
        
    def validate_connection_params(self, params):
        """Validate connection parameters"""
        required_fields = ["server", "domain", "username", "password", "base_dn"]
        missing_fields = []
        
        for field in required_fields:
            if not params.get(field):
                missing_fields.append(field.replace('_', ' ').title())
                
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
            
        # Validate port
        port = params.get('port', 636)
        if not isinstance(port, int) or port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
            
        return True, "Valid"
        
    def get_default_config(self):
        """Get default configuration"""
        return {
            "server": "",
            "port": 636,
            "use_ssl": True,
            "domain": "",
            "base_dn": "",
            "username": "",
            "auto_refresh": False,
            "refresh_interval": 300,
            "warning_days": 14
        }
        
    def format_user_data_for_export(self, users_data):
        """Format user data for export"""
        formatted_data = []
        
        for user in users_data:
            # Format dates
            last_set = user.get('password_last_set', '')
            if isinstance(last_set, datetime):
                last_set = last_set.strftime('%Y-%m-%d %H:%M')
                
            expires = user.get('password_expires', '')
            if user.get('password_never_expires', False):
                expires = "Never"
            elif isinstance(expires, datetime):
                expires = expires.strftime('%Y-%m-%d %H:%M')
                
            # Determine status
            days = user.get('days_until_expiry', 0)
            if user.get('account_disabled', False):
                status = "Disabled"
            elif user.get('password_never_expires', False):
                status = "Never Expires"
            elif days < 0:
                status = "Expired"
            elif days <= 7:
                status = "Expiring Soon"
            else:
                status = "Active"
                
            formatted_data.append({
                'username': user.get('username', ''),
                'display_name': user.get('display_name', ''),
                'email': user.get('email', ''),
                'days_until_expiry': days,
                'password_last_set': last_set,
                'password_expires': expires,
                'status': status
            })
            
        return formatted_data
        
    def get_status_summary(self, users_data):
        """Get status summary for users"""
        if not users_data:
            return {
                'total': 0,
                'expired': 0,
                'expiring_soon': 0,
                'active': 0,
                'never_expires': 0,
                'disabled': 0
            }
            
        total = len(users_data)
        expired = len([u for u in users_data if u.get('days_until_expiry', 0) < 0])
        expiring_soon = len([u for u in users_data if 0 <= u.get('days_until_expiry', 0) <= 7])
        never_expires = len([u for u in users_data if u.get('password_never_expires', False)])
        disabled = len([u for u in users_data if u.get('account_disabled', False)])
        active = total - expired - expiring_soon - never_expires - disabled
        
        return {
            'total': total,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'active': active,
            'never_expires': never_expires,
            'disabled': disabled
        }