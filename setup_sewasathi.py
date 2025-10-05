#!/usr/bin/env python3
"""
SewaSathi Billing Software Setup Script
Automated setup and launcher for SewaSathi billing system
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🌱 SewaSathi Billing Software Setup")
    print("   Har Kaam Ka Saathi – SewaSathi")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please install Python 3.7 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    required_packages = [
        'reportlab>=4.0.0',
        'qrcode[pil]>=7.0.0',
        'Pillow>=10.0.0'
    ]
    
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--user"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_gui_support():
    """Check if GUI (tkinter) is available"""
    print("\nChecking GUI support...")
    try:
        import tkinter
        print("✅ tkinter (GUI) is available")
        return True
    except ImportError:
        print("⚠️  tkinter (GUI) is not available")
        print("   The software will work in command-line mode only")
        print("   For full GUI support, install tkinter:")
        print("   - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   - CentOS/RHEL: sudo yum install tkinter")
        print("   - Windows: tkinter is included with Python")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        "SewaSathi_Bills",
        "SewaSathi_Backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_core_functionality():
    """Test core functionality"""
    print("\nTesting core functionality...")
    
    try:
        # Test imports
        import sqlite3
        import json
        import re
        from datetime import datetime
        print("✅ Core Python modules available")
        
        # Test installed packages
        import reportlab
        import qrcode
        from PIL import Image
        print("✅ PDF generation libraries available")
        
        # Test database creation
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()
        print("✅ Database functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if sys.platform.startswith('win'):
        print("\nCreating desktop shortcut...")
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "SewaSathi Billing.lnk")
            target = os.path.join(os.getcwd(), "sewasathi_billing.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✅ Desktop shortcut created")
        except ImportError:
            print("⚠️  Could not create desktop shortcut (winshell not available)")
        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")

def show_usage_instructions():
    """Show usage instructions"""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print()
    print("📋 How to use SewaSathi Billing Software:")
    print()
    print("1. Run the application:")
    print(f"   python3 {os.path.join(os.getcwd(), 'sewasathi_billing.py')}")
    print()
    print("2. Admin Login:")
    print("   - Default password: admin123")
    print("   - Change password in Admin Panel")
    print()
    print("3. Generate Bills:")
    print("   - Paste WhatsApp booking message")
    print("   - Click 'Parse Message'")
    print("   - Review and click 'Generate Bill'")
    print()
    print("4. Files and Folders:")
    print("   - Bills saved in: SewaSathi_Bills/")
    print("   - Database: sewasathi.db")
    print("   - Backups: SewaSathi_Backups/")
    print()
    print("📞 Support:")
    print("   - Check README.md for detailed instructions")
    print("   - Run test_core_only.py to verify functionality")
    print()
    print("🌱 Thank you for choosing SewaSathi!")
    print("   Har Kaam Ka Saathi – SewaSathi")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check GUI support
    gui_available = check_gui_support()
    
    # Create directories
    create_directories()
    
    # Test functionality
    if not test_core_functionality():
        print("\n❌ Core functionality test failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create desktop shortcut (Windows only)
    if sys.platform.startswith('win'):
        create_desktop_shortcut()
    
    # Show usage instructions
    show_usage_instructions()
    
    # Ask if user wants to launch the application
    print("\n" + "=" * 60)
    if gui_available:
        launch = input("Would you like to launch SewaSathi Billing Software now? (y/n): ")
        if launch.lower() in ['y', 'yes']:
            print("\nLaunching SewaSathi Billing Software...")
            try:
                subprocess.Popen([sys.executable, "sewasathi_billing.py"])
                print("✅ Application launched successfully!")
            except Exception as e:
                print(f"❌ Failed to launch application: {e}")
                print("You can manually run: python3 sewasathi_billing.py")
    else:
        print("GUI not available. You can still test core functionality:")
        print("python3 test_core_only.py")
    
    print("\nSetup completed! 🎉")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)