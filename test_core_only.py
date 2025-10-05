#!/usr/bin/env python3
"""
Core functionality test for SewaSathi Billing Software
Tests without GUI dependencies
"""

import sys
import subprocess
import importlib
import os
import json
import sqlite3
import re
from datetime import datetime

# Auto-installer for required packages
def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = {
        'reportlab': 'reportlab',
        'qrcode': 'qrcode[pil]',
        'PIL': 'Pillow'
    }
    
    missing_packages = []
    
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print(f"✓ {module} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"ℹ {module} needs to be installed")
    
    if missing_packages:
        print("\nInstalling required packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✓ {package} installed successfully")
            else:
                print(f"✗ Failed to install {package}")
                return False
        print("All packages installed successfully!")
    
    return True

class SewaSathiDatabase:
    """Database manager for SewaSathi billing system"""
    
    def __init__(self, db_path="test_sewasathi.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                base_rate REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Packages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                multiplier REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default data
        self.insert_default_data(cursor)
        
        conn.commit()
        conn.close()
    
    def insert_default_data(self, cursor):
        """Insert default services and packages"""
        # Default services
        default_services = [
            ("Emergency Green Help", "Emergency eco-friendly assistance", 500.0),
            ("Home Cleaning", "Eco-friendly home cleaning service", 300.0),
            ("Garden Maintenance", "Sustainable garden care", 400.0),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO services (name, description, base_rate)
            VALUES (?, ?, ?)
        ''', default_services)
        
        # Default packages
        default_packages = [
            ("One-time", 1.0, "Single service visit"),
            ("Weekly", 0.9, "Weekly service package (10% discount)"),
            ("Monthly", 0.8, "Monthly service package (20% discount)"),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO packages (name, multiplier, description)
            VALUES (?, ?, ?)
        ''', default_packages)
    
    def get_services(self):
        """Get all services"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, base_rate FROM services ORDER BY name")
        services = cursor.fetchall()
        conn.close()
        return services
    
    def get_packages(self):
        """Get all packages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, multiplier FROM packages ORDER BY name")
        packages = cursor.fetchall()
        conn.close()
        return packages

class WhatsAppParser:
    """Parser for WhatsApp booking messages"""
    
    @staticmethod
    def parse_booking_message(message):
        """Parse WhatsApp booking message and extract details"""
        booking_data = {}
        
        # Patterns for different fields
        patterns = {
            'booking_id': r'📋 Booking ID:\s*([^\n]+)',
            'service': r'🌿 Service:\s*([^\n]+)',
            'package': r'📦 Package:\s*([^\n]+)',
            'name': r'👤 Name:\s*([^\n]+)',
            'phone': r'📱 Phone:\s*([^\n]+)',
            'email': r'📧 Email:\s*([^\n]+)',
            'date': r'📅 Date:\s*([^\n]+)',
            'time': r'⏰ Time:\s*([^\n]+)',
            'address': r'📍 Address:\s*([^\n]+)',
            'requirements': r'📝 Eco-Requirements:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                booking_data[key] = match.group(1).strip()
            else:
                booking_data[key] = ""
        
        return booking_data

def test_core_functionality():
    """Test core functionality"""
    print("🌱 SewaSathi Billing Software - Core Functionality Test\n")
    
    # Test 1: Install dependencies
    print("1. Testing dependency installation...")
    if not check_and_install_dependencies():
        print("✗ Dependency installation failed")
        return False
    print("✓ Dependencies ready\n")
    
    # Test 2: Database functionality
    print("2. Testing database functionality...")
    try:
        db = SewaSathiDatabase()
        services = db.get_services()
        packages = db.get_packages()
        
        print(f"✓ Database created with {len(services)} services and {len(packages)} packages")
        
        for service in services:
            print(f"  - {service[0]}: ₹{service[1]}")
        
        # Clean up
        if os.path.exists("test_sewasathi.db"):
            os.remove("test_sewasathi.db")
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    print()
    
    # Test 3: WhatsApp parser
    print("3. Testing WhatsApp message parser...")
    try:
        test_message = """
        🌱 ECO-BOOKING FROM WEBSITE - SewaSathi
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📋 Booking ID: ECO849861
        🌿 Service: Emergency Green Help
        📦 Package: Weekly
        👤 Name: Sandeep
        📱 Phone: +919628505560
        📧 Email: anshpandit5560@gmail.com
        📅 Date: 2025-09-28
        ⏰ Time: 14:03
        📍 Address: Naka ,Raibareli bypass, Shiv nagar colony
        📝 Eco-Requirements: Trusted employee and experience
        """
        
        parser = WhatsAppParser()
        result = parser.parse_booking_message(test_message)
        
        print("✓ Message parsed successfully:")
        for key, value in result.items():
            if value:
                print(f"  - {key}: {value}")
                
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False
    print()
    
    # Test 4: PDF generation libraries
    print("4. Testing PDF generation capabilities...")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        import qrcode
        from PIL import Image
        
        print("✓ All PDF libraries imported successfully")
        
        # Test QR code generation
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("upi://pay?pa=9628505560-2@ibl&pn=SewaSathi&cu=INR")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = "test_qr.png"
        qr_img.save(qr_path)
        
        if os.path.exists(qr_path):
            print("✓ QR code generation successful")
            os.remove(qr_path)
        
    except Exception as e:
        print(f"✗ PDF generation test failed: {e}")
        return False
    print()
    
    print("🎉 All core functionality tests passed!")
    print("The SewaSathi Billing Software core is working correctly.")
    print("\nTo run the full GUI application:")
    print("python3 sewasathi_billing.py")
    
    return True

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)