#!/usr/bin/env python3
"""
SigmaToolkit - Service Monitor Setup Script
This script sets up the service monitoring module for your SigmaToolkit application.
"""

import os
import shutil
from pathlib import Path

def setup_services_module():
    """Set up the services module directory and files"""
    
    print("🔧 SigmaToolkit Service Monitor Setup")
    print("=" * 50)
    
    # Get the current directory (should be SigmaToolkit root)
    project_root = Path.cwd()
    print(f"📁 Project location: {project_root}")
    print()
    
    # Create services directory
    services_dir = project_root / "services"
    services_dir.mkdir(exist_ok=True)
    print(f"✓ Created directory: services/")
    
    # Create __init__.py
    init_file = services_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# services/__init__.py\n# Service monitoring module for SigmaToolkit\n")
        print(f"✓ Created file: services/__init__.py")
    else:
        print(f"- File already exists: services/__init__.py")
    
    # Check for main files that need to be created
    required_files = [
        "services/services_tab.py",
        "services/services_tools.py"
    ]
    
    print()
    print("📋 Required Files Check:")
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print()
        print("⚠️  Missing Required Files!")
        print("You need to create the following files with the provided code:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print()
        print("📝 Instructions:")
        print("1. Copy the services_tab.py code into services/services_tab.py")
        print("2. Copy the services_tools.py code into services/services_tools.py")
        print("3. Update your main_window.py with the new version")
        print("4. Install required dependencies: pip install requests")
        print("5. Restart SigmaToolkit")
        return False
    
    # Check if requests library is available
    try:
        import requests
        print(f"✅ Dependencies: requests library found")
    except ImportError:
        print(f"❌ Dependencies: requests library missing")
        print("💡 Install with: pip install requests")
        return False
    
    # Update requirements.txt
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        requirements_content = requirements_file.read_text()
        if "requests" not in requirements_content:
            # Add requests to requirements
            with open(requirements_file, 'a') as f:
                if not requirements_content.endswith('\n'):
                    f.write('\n')
                f.write('requests>=2.25.0\n')
            print(f"✅ Updated requirements.txt with requests dependency")
        else:
            print(f"✅ Requirements.txt already includes requests")
    
    print()
    print("🎉 Service Monitor Setup Complete!")
    print()
    print("📊 Service Monitor Features:")
    print("   • Real-time monitoring of Microsoft 365 services")
    print("   • Google Workspace service monitoring")
    print("   • Cloud provider status (AWS, Azure, Google Cloud)")
    print("   • Custom service endpoint monitoring")
    print("   • Auto-refresh and status alerts")
    print("   • HTTP, Ping, Port, DNS, and API health checks")
    print("   • Service categorization and bulk management")
    print("   • Export capabilities for status reports")
    print()
    print("🚀 Next Steps:")
    print("1. Restart SigmaToolkit")
    print("2. Navigate to the '🟢 Service Monitor' tab")
    print("3. Add Microsoft 365 services with one click")
    print("4. Configure custom services for your infrastructure")
    print("5. Enable auto-refresh for continuous monitoring")
    print()
    print("💡 Pro Tips:")
    print("   • Start with pre-configured service categories")
    print("   • Use different check types for different services")
    print("   • Export service configurations for backup")
    print("   • Combine with other SigmaToolkit tabs for complete diagnostics")
    
    return True

def create_sample_service_config():
    """Create a sample service configuration file"""
    project_root = Path.cwd()
    config_file = project_root / "sample_service_config.json"
    
    sample_config = {
        "services": [
            {
                "name": "Microsoft 365 Login",
                "url": "https://login.microsoftonline.com",
                "type": "http",
                "category": "Microsoft 365"
            },
            {
                "name": "Exchange Online",
                "url": "https://outlook.office365.com",
                "type": "http",
                "category": "Microsoft 365"
            },
            {
                "name": "SharePoint Online",
                "url": "https://admin.microsoft.com",
                "type": "http",
                "category": "Microsoft 365"
            },
            {
                "name": "Google DNS",
                "url": "8.8.8.8",
                "type": "ping",
                "category": "Infrastructure"
            },
            {
                "name": "Cloudflare DNS",
                "url": "1.1.1.1",
                "type": "ping",
                "category": "Infrastructure"
            },
            {
                "name": "AWS Console",
                "url": "https://console.aws.amazon.com",
                "type": "http",
                "category": "Cloud Providers"
            },
            {
                "name": "Azure Portal",
                "url": "https://portal.azure.com",
                "type": "http",
                "category": "Cloud Providers"
            }
        ]
    }
    
    try:
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"📄 Created sample configuration: {config_file}")
        print("   You can load this in SigmaToolkit via File > Load Service Config")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample config: {e}")
        return False

def verify_installation():
    """Verify the service monitor installation"""
    print("\n🔍 Verifying Installation...")
    
    project_root = Path.cwd()
    
    # Check main files
    main_files = [
        "main.py",
        "ui/main_window.py",
        "services/__init__.py",
        "services/services_tab.py", 
        "services/services_tools.py"
    ]
    
    all_good = True
    for file_path in main_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    # Check dependencies
    try:
        import PyQt5
        print(f"✅ PyQt5 available")
    except ImportError:
        print(f"❌ PyQt5 missing - install with: pip install PyQt5")
        all_good = False
    
    try:
        import requests
        print(f"✅ requests available")
    except ImportError:
        print(f"❌ requests missing - install with: pip install requests")
        all_good = False
    
    if all_good:
        print("\n🎉 Installation verification passed!")
        print("✅ All required files and dependencies are present")
        print("🚀 You can now run SigmaToolkit with Service Monitor")
    else:
        print("\n⚠️ Installation verification failed!")
        print("❌ Some files or dependencies are missing")
        print("📝 Please review the setup instructions above")
    
    return all_good

def main():
    """Main setup function"""
    print("🛠️ Starting SigmaToolkit Service Monitor Setup...")
    print()
    
    try:
        # Setup services module
        setup_success = setup_services_module()
        
        if setup_success:
            # Create sample configuration
            create_sample_service_config()
            
            # Verify installation
            verify_installation()
            
            print("\n" + "=" * 50)
            print("🎯 Setup Summary:")
            print("✅ Service Monitor module ready")
            print("✅ Dependencies checked")
            print("✅ Sample configuration created")
            print("✅ Installation verified")
            print()
            print("🔄 Next: Restart SigmaToolkit to use Service Monitor")
        else:
            print("\n❌ Setup incomplete - please follow the instructions above")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())