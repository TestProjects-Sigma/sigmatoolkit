# Quick test to check if LAN tools are working
# Save this as test_lan_import.py and run it to check

import sys
import os

print("🔍 Testing LAN Tools Import...")
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print()

try:
    from speedtest.lan_speed_tools import LANSpeedTools
    print("✅ SUCCESS: LANSpeedTools imported successfully!")
    print("✨ Advanced LAN testing should be available")
    
    # Test creating an instance
    class DummyLogger:
        def debug(self, msg): pass
        def error(self, msg): pass
    
    lan_tools = LANSpeedTools(DummyLogger())
    print("✅ LANSpeedTools instance created successfully")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("💡 Make sure lan_speed_tools.py is in the speedtest/ directory")
    
except Exception as e:
    print(f"❌ OTHER ERROR: {e}")

print()
print("📁 Checking file structure...")

# Check if files exist
files_to_check = [
    "speedtest/lan_speed_tools.py",
    "speedtest/speedtest_tab.py", 
    "speedtest/speedtest_tools.py",
    "speedtest/__init__.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✅ {file_path} exists")
    else:
        print(f"❌ {file_path} MISSING")

print()
print("🔧 If files are missing:")
print("1. Create speedtest/lan_speed_tools.py with the Advanced LAN Testing code")
print("2. Replace speedtest/speedtest_tab.py with the updated version")
print("3. Restart SigmaToolkit")
print()
print("If files exist but import fails, check for syntax errors in the files.")