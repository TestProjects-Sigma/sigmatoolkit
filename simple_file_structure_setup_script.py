#!/usr/bin/env python3
"""
IT Troubleshoot Tool - Simple File Structure Creator
This script creates empty files and folders for the project structure.
"""

import os
from pathlib import Path

def create_project_structure():
    """Create the project directory structure with empty files"""
    
    # Project root directory
    project_name = "it_troubleshoot_tool"
    base_path = Path.cwd() / project_name
    
    print(f"Creating IT Troubleshoot Tool file structure...")
    print(f"Project location: {base_path}")
    print()
    
    # Define the complete file structure
    files_and_folders = [
        # Root files
        "main.py",
        "requirements.txt", 
        "README.md",
        
        # Config folder and files
        "config/__init__.py",
        "config/settings.py",
        
        # Core folder and files
        "core/__init__.py",
        "core/base_tab.py",
        "core/logger.py",
        
        # Network folder and files
        "network/__init__.py",
        "network/network_tab.py",
        "network/network_tools.py",
        
        # DNS folder and files
        "dns/__init__.py",
        "dns/dns_tab.py",
        "dns/dns_tools.py",
        
        # SMTP folder and files
        "smtp/__init__.py",
        "smtp/smtp_tab.py",
        "smtp/smtp_tools.py",
        
        # Speedtest folder and files (NEW in v1.3.0)
        "speedtest/__init__.py",
        "speedtest/speedtest_tab.py",
        "speedtest/speedtest_tools.py",
        
        # UI folder and files
        "ui/__init__.py",
        "ui/main_window.py"
    ]
    
    # Create the base project directory
    base_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {project_name}/")
    
    # Create all files and their parent directories
    for file_path in files_and_folders:
        full_path = base_path / file_path
        
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file
        if not full_path.exists():
            full_path.touch()
            print(f"✓ Created file: {file_path}")
        else:
            print(f"- File already exists: {file_path}")
    
    print()
    print("🎉 File structure created successfully!")
    print()
    print("📁 Your project structure:")
    print("SigmaToolkit/")
    print("├── main.py")
    print("├── requirements.txt")
    print("├── README.md")
    print("├── config/")
    print("│   ├── __init__.py")
    print("│   └── settings.py")
    print("├── core/")
    print("│   ├── __init__.py")
    print("│   ├── base_tab.py")
    print("│   └── logger.py")
    print("├── network/")
    print("│   ├── __init__.py")
    print("│   ├── network_tab.py")
    print("│   └── network_tools.py")
    print("├── dns/")
    print("│   ├── __init__.py")
    print("│   ├── dns_tab.py")
    print("│   └── dns_tools.py")
    print("├── smtp/")
    print("│   ├── __init__.py")
    print("│   ├── smtp_tab.py")
    print("│   └── smtp_tools.py")
    print("├── speedtest/")
    print("│   ├── __init__.py")
    print("│   ├── speedtest_tab.py")
    print("│   └── speedtest_tools.py")
    print("└── ui/")
    print("    ├── __init__.py")
    print("    └── main_window.py")
    print()
    print("📝 Next steps:")
    print("1. Copy and paste the code into each file")
    print("2. Install dependencies: pip install PyQt5")
    print("3. Run the application: python main.py")
    
    return base_path

def main():
    """Main function"""
    print("=" * 50)
    print("  IT Troubleshoot Tool - Structure Creator")
    print("=" * 50)
    print()
    
    try:
        create_project_structure()
    except Exception as e:
        print(f"❌ Error creating structure: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())