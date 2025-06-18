# portlistener/port_listener_tools.py
import socket
import threading
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class PortListenerTools(QObject):
    connection_received = pyqtSignal(str, str)  # client_ip, timestamp
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # uptime
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.listening = False
        self.socket = None
        self.listen_thread = None
        self.start_time = None
        self.connection_count = 0
        self.last_client_ip = None
        
        # Timer for uptime updates
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        
    def start_listening(self, ip, port, response_type="HTTP OK"):
        """Start listening on the specified IP and port"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(1.0)  # Allow checking for stop condition
            
            bind_ip = "" if ip == "0.0.0.0" else ip
            self.socket.bind((bind_ip, port))
            self.socket.listen(5)
            
            self.listening = True
            self.start_time = datetime.now()
            self.connection_count = 0
            self.response_type = response_type
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            # Start uptime timer
            self.uptime_timer.start(1000)  # Update every second
            
            self.logger.debug(f"Port listener started on {ip}:{port}")
            return True
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.logger.error(f"Failed to start port listener: {str(e)}")
            return False
            
    def stop_listening(self):
        """Stop the port listener"""
        try:
            self.listening = False
            self.uptime_timer.stop()
            
            if self.socket:
                self.socket.close()
                self.socket = None
                
            if self.listen_thread and self.listen_thread.is_alive():
                self.listen_thread.join(timeout=3)
                
            self.logger.debug("Port listener stopped")
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.logger.error(f"Error stopping port listener: {str(e)}")
            
    def _listen_loop(self):
        """Main listening loop"""
        while self.listening and self.socket:
            try:
                conn, addr = self.socket.accept()
                self.connection_count += 1
                self.last_client_ip = addr[0]
                
                # Handle the connection
                self._handle_connection(conn, addr)
                
                # Emit signal
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.connection_received.emit(addr[0], timestamp)
                
            except socket.timeout:
                continue  # Check if we should keep listening
            except Exception as e:
                if self.listening:  # Only log if we're supposed to be listening
                    self.error_occurred.emit(f"Connection handling error: {str(e)}")
                break
                
    def _handle_connection(self, conn, addr):
        """Handle an individual connection"""
        try:
            # Receive any data (optional)
            try:
                data = conn.recv(1024)
                if data:
                    self.logger.debug(f"Received data from {addr[0]}: {data[:100]}")
            except:
                pass
                
            # Send response based on type
            if self.response_type == "HTTP OK":
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 23\r\n\r\nPort test successful!"
                conn.send(response)
            elif self.response_type == "Echo":
                if data:
                    conn.send(b"ECHO: " + data)
                else:
                    conn.send(b"ECHO: No data received")
            # Silent mode sends no response
            
        except Exception as e:
            self.logger.debug(f"Error handling connection from {addr[0]}: {str(e)}")
        finally:
            try:
                conn.close()
            except:
                pass
                
    def test_connection(self, ip, port):
        """Test connection to the specified IP and port"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(5)
            
            result = test_socket.connect_ex((ip, port))
            test_socket.close()
            
            return result == 0
            
        except Exception as e:
            self.logger.debug(f"Test connection error: {str(e)}")
            return False
            
    def get_statistics(self):
        """Get current statistics"""
        return {
            'connections': self.connection_count,
            'last_client': self.last_client_ip,
            'uptime': self._get_uptime_string(),
            'listening': self.listening
        }
        
    def update_uptime(self):
        """Update uptime display"""
        if self.listening and self.start_time:
            uptime = self._get_uptime_string()
            self.status_changed.emit(uptime)
            
    def _get_uptime_string(self):
        """Get formatted uptime string"""
        if not self.start_time:
            return "00:00:00"
            
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        seconds = int(uptime.total_seconds() % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"