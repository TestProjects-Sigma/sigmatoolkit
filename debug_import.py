# debug_import.py - Test script to debug import issues
import sys
import os

print("=" * 50)
print("SigmaToolkit Port Listener Import Debug")
print("=" * 50)

# Check current working directory
print(f"Current working directory: {os.getcwd()}")

# Check if portlistener directory exists
portlistener_path = "portlistener"
if os.path.exists(portlistener_path):
    print(f"✅ {portlistener_path} directory exists")
    
    # Check files in portlistener directory
    files = os.listdir(portlistener_path)
    print(f"Files in {portlistener_path}: {files}")
    
    # Check specific files
    required_files = ["__init__.py", "port_listener_tab.py", "port_listener_tools.py"]
    for file in required_files:
        file_path = os.path.join(portlistener_path, file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
            # Check file size
            size = os.path.getsize(file_path)
            print(f"   Size: {size} bytes")
        else:
            print(f"❌ {file} missing")
else:
    print(f"❌ {portlistener_path} directory not found")

print("\n" + "=" * 30)
print("Testing Import")
print("=" * 30)

# Test basic module import
try:
    import portlistener
    print("✅ portlistener module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import portlistener module: {e}")

# Test core modules that port listener depends on
try:
    from core.base_tab import BaseTab
    print("✅ core.base_tab imported successfully")
except ImportError as e:
    print(f"❌ Failed to import core.base_tab: {e}")

try:
    from core.logger import Logger
    print("✅ core.logger imported successfully")
except ImportError as e:
    print(f"❌ Failed to import core.logger: {e}")

# Test PyQt5 imports
try:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import QObject, pyqtSignal
    print("✅ PyQt5 imports successful")
except ImportError as e:
    print(f"❌ Failed to import PyQt5: {e}")

# Test port listener tools import
try:
    from portlistener.port_listener_tools import PortListenerTools
    print("✅ PortListenerTools imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PortListenerTools: {e}")
    print(f"   Detailed error: {type(e).__name__}: {e}")

# Test port listener tab import
try:
    from portlistener.port_listener_tab import PortListenerTab
    print("✅ PortListenerTab imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PortListenerTab: {e}")
    print(f"   Detailed error: {type(e).__name__}: {e}")

print("\n" + "=" * 30)
print("Python Path")
print("=" * 30)
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")

print("\n" + "=" * 30)
print("Recommendations")
print("=" * 30)

if not os.path.exists("portlistener"):
    print("1. Create the 'portlistener' directory in your project root")
    
if not os.path.exists("portlistener/__init__.py"):
    print("2. Create 'portlistener/__init__.py' file (can be empty)")
    
print("3. Make sure you're running this script from the project root directory")
print("4. Ensure all files have the correct Python syntax")
print("5. Check that core modules (base_tab.py, logger.py) exist and work")

print("\n" + "=" * 50)