#!/usr/bin/env python3
"""
SigmaToolkit - GitHub Cleanup Script
This script cleans up the project directory before uploading to GitHub
"""

import os
import shutil
from pathlib import Path
import fnmatch

def clean_project():
    """Clean up project directory for GitHub upload"""
    
    print("🧹 SigmaToolkit GitHub Cleanup Script")
    print("=" * 50)
    
    # Get the current directory (should be SigmaToolkit root)
    project_root = Path.cwd()
    print(f"📁 Cleaning project: {project_root.name}")
    print()
    
    # Files and directories to remove
    cleanup_patterns = [
        # Python cache files
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        ".Python",
        
        # IDE and editor files
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        "*~",
        ".DS_Store",
        "Thumbs.db",
        
        # Virtual environment directories
        "venv",
        "env",
        ".env",
        "ENV",
        
        # Build and distribution directories
        "build",
        "dist",
        "*.egg-info",
        ".eggs",
        
        # Testing and coverage
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".tox",
        
        # Logs and temporary files
        "*.log",
        "*.tmp",
        ".temp",
        "temp",
        
        # OS and system files
        ".Trash-*",
        "ehthumbs.db",
        "Desktop.ini",
        
        # Application specific
        "settings.json",  # User settings file
        ".SigmaToolkit",  # User config directory
    ]
    
    removed_count = 0
    
    # Clean up files and directories
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        
        # Skip if we're in .git directory
        if '.git' in root_path.parts:
            continue
            
        # Check directories
        for dir_name in dirs[:]:  # Use slice to modify list while iterating
            for pattern in cleanup_patterns:
                if fnmatch.fnmatch(dir_name, pattern):
                    dir_path = root_path / dir_name
                    try:
                        shutil.rmtree(dir_path)
                        print(f"🗑️  Removed directory: {dir_path.relative_to(project_root)}")
                        removed_count += 1
                        dirs.remove(dir_name)  # Don't traverse into removed directory
                    except Exception as e:
                        print(f"❌ Error removing {dir_path}: {e}")
                    break
        
        # Check files
        for file_name in files:
            for pattern in cleanup_patterns:
                if fnmatch.fnmatch(file_name, pattern):
                    file_path = root_path / file_name
                    try:
                        file_path.unlink()
                        print(f"🗑️  Removed file: {file_path.relative_to(project_root)}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Error removing {file_path}: {e}")
                    break
    
    print()
    
    # Check for empty directories and remove them
    empty_dirs_removed = 0
    for root, dirs, files in os.walk(project_root, topdown=False):
        root_path = Path(root)
        
        # Skip git and project root
        if '.git' in root_path.parts or root_path == project_root:
            continue
            
        # If directory is empty, remove it
        try:
            if not any(root_path.iterdir()):
                root_path.rmdir()
                print(f"📁 Removed empty directory: {root_path.relative_to(project_root)}")
                empty_dirs_removed += 1
        except Exception:
            pass  # Directory not empty or other error
    
    # Create .gitignore if it doesn't exist
    gitignore_path = project_root / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Logs
*.log

# Application specific
settings.json
.SigmaToolkit/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
"""
        try:
            gitignore_path.write_text(gitignore_content)
            print(f"📝 Created .gitignore file")
        except Exception as e:
            print(f"❌ Error creating .gitignore: {e}")
    
    # Verify core files exist
    print()
    print("🔍 Verifying core project files...")
    core_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "core/base_tab.py",
        "core/logger.py",
        "network/network_tab.py",
        "network/network_tools.py",
        "dns/dns_tab.py",
        "dns/dns_tools.py",
        "ui/main_window.py"
    ]
    
    missing_files = []
    for file_path in core_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
            print(f"⚠️  Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    # Summary
    print()
    print("📊 Cleanup Summary:")
    print(f"   🗑️  Removed {removed_count} files/directories")
    print(f"   📁 Removed {empty_dirs_removed} empty directories")
    print(f"   📝 .gitignore: {'Created' if not gitignore_path.exists() else 'Already exists'}")
    
    if missing_files:
        print(f"   ⚠️  {len(missing_files)} core files missing")
        print("      Please ensure all required files are present before uploading")
    else:
        print(f"   ✅ All core files present")
    
    print()
    
    if removed_count > 0 or empty_dirs_removed > 0:
        print("✨ Project cleaned successfully! Ready for GitHub upload.")
    else:
        print("✨ Project was already clean! Ready for GitHub upload.")
    
    # Show final project structure
    print()
    print("📁 Final project structure:")
    show_tree(project_root, max_depth=3)

def show_tree(path, prefix="", max_depth=3, current_depth=0):
    """Display directory tree structure"""
    if current_depth >= max_depth:
        return
        
    path = Path(path)
    if not path.is_dir():
        return
        
    items = sorted([p for p in path.iterdir() if not p.name.startswith('.git')])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            show_tree(item, prefix + extension, max_depth, current_depth + 1)

def main():
    """Main cleanup function"""
    try:
        clean_project()
        print()
        print("🎯 Next steps:")
        print("   1. Review the cleaned project")
        print("   2. Test the application: python main.py") 
        print("   3. Add to git: git add .")
        print("   4. Commit: git commit -m 'Initial release: SigmaToolkit v1.1.0'")
        print("   5. Push to GitHub: git push origin main")
        print()
        print("🚀 Happy coding!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Cleanup cancelled by user")
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())