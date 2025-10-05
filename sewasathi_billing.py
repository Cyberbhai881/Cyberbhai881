#!/usr/bin/env python3
"""
SewaSathi Billing Software
Professional billing system for SewaSathi services
Author: AI Assistant
Version: 1.0
"""

import sys
import subprocess
import importlib
import os
import json
import sqlite3
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import webbrowser
import tempfile
import shutil
from pathlib import Path

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
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing required packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✓ {package} installed successfully")
            else:
                print(f"✗ Failed to install {package}")
                return False
        print("All packages installed successfully!")
        
        # Restart the script to load newly installed packages
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    return True

# Install dependencies first
if __name__ == "__main__":
    check_and_install_dependencies()

# Import required libraries after installation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import qrcode
from PIL import Image as PILImage, ImageDraw, ImageFont

class SewaSathiDatabase:
    """Database manager for SewaSathi billing system"""
    
    def __init__(self, db_path="sewasathi.db"):
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
        
        # Bills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_no TEXT NOT NULL UNIQUE,
                booking_id TEXT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                customer_email TEXT,
                customer_address TEXT,
                service_name TEXT NOT NULL,
                package_name TEXT NOT NULL,
                service_date TEXT,
                service_time TEXT,
                base_amount REAL NOT NULL,
                extra_charges REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                tax_rate REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                requirements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Admin settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
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
            ("Pest Control", "Organic pest control solutions", 600.0),
            ("Plumbing Service", "Water-efficient plumbing solutions", 350.0),
            ("Electrical Service", "Energy-efficient electrical work", 450.0)
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
            ("Quarterly", 0.75, "Quarterly service package (25% discount)"),
            ("Yearly", 0.7, "Yearly service package (30% discount)")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO packages (name, multiplier, description)
            VALUES (?, ?, ?)
        ''', default_packages)
        
        # Default admin password
        cursor.execute('''
            INSERT OR IGNORE INTO admin_settings (key, value)
            VALUES ('admin_password', 'admin123')
        ''')
        
        # Default tax rate
        cursor.execute('''
            INSERT OR IGNORE INTO admin_settings (key, value)
            VALUES ('tax_rate', '18.0')
        ''')
    
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
    
    def add_service(self, name, description, base_rate):
        """Add a new service"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO services (name, description, base_rate)
                VALUES (?, ?, ?)
            ''', (name, description, base_rate))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def add_package(self, name, multiplier, description):
        """Add a new package"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO packages (name, multiplier, description)
                VALUES (?, ?, ?)
            ''', (name, multiplier, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def save_bill(self, bill_data):
        """Save bill to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bills (
                bill_no, booking_id, customer_name, customer_phone, customer_email,
                customer_address, service_name, package_name, service_date, service_time,
                base_amount, extra_charges, discount, tax_rate, tax_amount, total_amount,
                requirements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', bill_data)
        conn.commit()
        conn.close()
    
    def get_admin_setting(self, key):
        """Get admin setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_admin_setting(self, key, value):
        """Set admin setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO admin_settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()

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

class PDFGenerator:
    """PDF bill generator for SewaSathi"""
    
    def __init__(self):
        self.company_name = "SewaSathi"
        self.company_slogan = "Har Kaam Ka Saathi – SewaSathi"
        self.upi_id = "9628505560-2@ibl"
        self.create_logo()
    
    def create_logo(self):
        """Create a simple logo placeholder"""
        logo_path = "sewasathi_logo.png"
        if not os.path.exists(logo_path):
            # Create a simple logo
            img = PILImage.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple eco-friendly design
            draw.rectangle([10, 10, 190, 90], outline='green', width=3)
            draw.ellipse([20, 20, 80, 80], fill='lightgreen')
            draw.text((90, 35), "SewaSathi", fill='green')
            draw.text((90, 55), "🌱 Eco Service", fill='darkgreen')
            
            img.save(logo_path)
        
        return logo_path
    
    def generate_qr_code(self, upi_string):
        """Generate QR code for UPI payment"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"upi://pay?pa={self.upi_id}&pn=SewaSathi&cu=INR")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = "temp_qr.png"
        qr_img.save(qr_path)
        return qr_path
    
    def generate_bill(self, bill_data, filename):
        """Generate professional PDF bill"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.green
        )
        
        # Header with logo and company info
        header_data = [
            [Image(self.create_logo(), width=100, height=50), 
             Paragraph(f"<b>{self.company_name}</b>", title_style)],
            ["", Paragraph(self.company_slogan, subtitle_style)]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Bill header
        bill_header = f"<b>INVOICE #{bill_data['bill_no']}</b>"
        story.append(Paragraph(bill_header, styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Date and time
        date_time = f"Date: {datetime.now().strftime('%d-%m-%Y')} | Time: {datetime.now().strftime('%H:%M:%S')}"
        story.append(Paragraph(date_time, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Customer details
        customer_data = [
            ["Customer Details", ""],
            ["Name:", bill_data.get('customer_name', '')],
            ["Phone:", bill_data.get('customer_phone', '')],
            ["Email:", bill_data.get('customer_email', '')],
            ["Address:", bill_data.get('customer_address', '')],
            ["Booking ID:", bill_data.get('booking_id', '')],
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(customer_table)
        story.append(Spacer(1, 20))
        
        # Service details
        service_data = [
            ["Service Details", "", "", ""],
            ["Service", "Package", "Date", "Time"],
            [bill_data.get('service_name', ''), 
             bill_data.get('package_name', ''),
             bill_data.get('service_date', ''),
             bill_data.get('service_time', '')]
        ]
        
        service_table = Table(service_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (3, 1), colors.grey),
            ('TEXTCOLOR', (0, 1), (3, 1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(service_table)
        story.append(Spacer(1, 20))
        
        # Billing details
        billing_data = [
            ["Billing Details", "Amount (₹)"],
            ["Base Service Charge", f"₹{bill_data.get('base_amount', 0):.2f}"],
            ["Extra Charges", f"₹{bill_data.get('extra_charges', 0):.2f}"],
            ["Discount", f"-₹{bill_data.get('discount', 0):.2f}"],
            ["Tax Amount", f"₹{bill_data.get('tax_amount', 0):.2f}"],
            ["Total Amount", f"₹{bill_data.get('total_amount', 0):.2f}"]
        ]
        
        billing_table = Table(billing_data, colWidths=[4*inch, 2*inch])
        billing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 5), (1, 5), colors.darkgreen),
            ('TEXTCOLOR', (0, 5), (1, 5), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, 4), [colors.beige, colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(billing_table)
        story.append(Spacer(1, 30))
        
        # Payment QR Code
        qr_path = self.generate_qr_code(self.upi_id)
        payment_data = [
            ["Payment via UPI", ""],
            [Image(qr_path, width=100, height=100), 
             f"UPI ID: {self.upi_id}\n\nScan QR code to pay\nusing any UPI app"]
        ]
        
        payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(payment_table)
        story.append(Spacer(1, 30))
        
        # Terms and conditions
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.darkred
        )
        
        story.append(Paragraph("<b>Terms & Conditions:</b>", styles['Heading3']))
        story.append(Paragraph("• No Service, No Payment", terms_style))
        story.append(Paragraph("• No Work, No Payment", terms_style))
        story.append(Spacer(1, 20))
        
        # Thank you note
        thank_you_style = ParagraphStyle(
            'ThankYou',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        )
        
        story.append(Paragraph("🙏 Thank You for Choosing SewaSathi! We look forward to serving you again.", thank_you_style))
        
        # Build PDF
        doc.build(story)
        
        # Clean up temporary files
        if os.path.exists(qr_path):
            os.remove(qr_path)
        
        return filename

class SewaSathiGUI:
    """Main GUI application for SewaSathi billing system"""
    
    def __init__(self):
        self.db = SewaSathiDatabase()
        self.parser = WhatsAppParser()
        self.pdf_generator = PDFGenerator()
        self.is_admin_logged_in = False
        
        # Create bills directory
        self.bills_dir = "SewaSathi_Bills"
        os.makedirs(self.bills_dir, exist_ok=True)
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root = tk.Tk()
        self.root.title("SewaSathi Billing Software")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f8f0')  # Light green background
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Green.TButton', background='#4CAF50', foreground='white')
        style.configure('Blue.TButton', background='#2196F3', foreground='white')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = tk.Label(main_frame, text="🌱 SewaSathi Billing System", 
                              font=('Arial', 24, 'bold'), 
                              fg='#2E7D32', bg='#f0f8f0')
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        subtitle_label = tk.Label(main_frame, text="Har Kaam Ka Saathi – SewaSathi", 
                                 font=('Arial', 12), 
                                 fg='#4CAF50', bg='#f0f8f0')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Admin login button
        admin_btn = ttk.Button(main_frame, text="Admin Login", 
                              command=self.admin_login, style='Blue.TButton')
        admin_btn.grid(row=2, column=2, sticky=tk.E, pady=10)
        
        # WhatsApp message input
        msg_frame = ttk.LabelFrame(main_frame, text="WhatsApp Booking Message", padding="10")
        msg_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.message_text = tk.Text(msg_frame, height=8, width=80, wrap=tk.WORD)
        self.message_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        parse_btn = ttk.Button(msg_frame, text="Parse Message", 
                              command=self.parse_message, style='Green.TButton')
        parse_btn.grid(row=1, column=0, pady=10)
        
        clear_btn = ttk.Button(msg_frame, text="Clear", command=self.clear_message)
        clear_btn.grid(row=1, column=1, pady=10, padx=10)
        
        # Customer details frame
        customer_frame = ttk.LabelFrame(main_frame, text="Customer Details", padding="10")
        customer_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Customer fields
        self.customer_fields = {}
        fields = [
            ("Booking ID:", "booking_id"),
            ("Customer Name:", "customer_name"),
            ("Phone:", "customer_phone"),
            ("Email:", "customer_email"),
            ("Address:", "customer_address"),
            ("Requirements:", "requirements")
        ]
        
        for i, (label, field) in enumerate(fields):
            tk.Label(customer_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(customer_frame, width=40)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
            self.customer_fields[field] = entry
        
        # Service details frame
        service_frame = ttk.LabelFrame(main_frame, text="Service Details", padding="10")
        service_frame.grid(row=4, column=2, sticky=(tk.W, tk.E, tk.N), pady=10, padx=10)
        
        # Service selection
        tk.Label(service_frame, text="Service:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.service_var = tk.StringVar()
        self.service_combo = ttk.Combobox(service_frame, textvariable=self.service_var, width=25)
        self.service_combo.grid(row=0, column=1, pady=2, padx=5)
        self.service_combo.bind('<<ComboboxSelected>>', self.update_service_rate)
        
        # Package selection
        tk.Label(service_frame, text="Package:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.package_var = tk.StringVar()
        self.package_combo = ttk.Combobox(service_frame, textvariable=self.package_var, width=25)
        self.package_combo.grid(row=1, column=1, pady=2, padx=5)
        self.package_combo.bind('<<ComboboxSelected>>', self.calculate_total)
        
        # Date and time
        tk.Label(service_frame, text="Service Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.service_date = tk.Entry(service_frame, width=25)
        self.service_date.grid(row=2, column=1, pady=2, padx=5)
        
        tk.Label(service_frame, text="Service Time:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.service_time = tk.Entry(service_frame, width=25)
        self.service_time.grid(row=3, column=1, pady=2, padx=5)
        
        # Billing frame
        billing_frame = ttk.LabelFrame(main_frame, text="Billing Details", padding="10")
        billing_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Billing fields
        billing_fields = [
            ("Base Amount (₹):", "base_amount"),
            ("Extra Charges (₹):", "extra_charges"),
            ("Discount (₹):", "discount"),
            ("Tax Rate (%):", "tax_rate"),
            ("Tax Amount (₹):", "tax_amount"),
            ("Total Amount (₹):", "total_amount")
        ]
        
        self.billing_fields = {}
        for i, (label, field) in enumerate(billing_fields):
            col = i % 3
            row = i // 3
            
            tk.Label(billing_frame, text=label).grid(row=row*2, column=col*2, sticky=tk.W, pady=2)
            entry = tk.Entry(billing_frame, width=15)
            entry.grid(row=row*2+1, column=col*2, sticky=tk.W, pady=2, padx=5)
            self.billing_fields[field] = entry
            
            if field in ["extra_charges", "discount", "tax_rate"]:
                entry.bind('<KeyRelease>', lambda e: self.calculate_total())
        
        # Set default tax rate
        tax_rate = self.db.get_admin_setting('tax_rate') or '18.0'
        self.billing_fields['tax_rate'].insert(0, tax_rate)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        generate_btn = ttk.Button(button_frame, text="Generate Bill", 
                                 command=self.generate_bill, style='Green.TButton')
        generate_btn.grid(row=0, column=0, padx=10)
        
        print_btn = ttk.Button(button_frame, text="Print Bill", 
                              command=self.print_bill)
        print_btn.grid(row=0, column=1, padx=10)
        
        whatsapp_btn = ttk.Button(button_frame, text="Share via WhatsApp", 
                                 command=self.share_whatsapp, style='Blue.TButton')
        whatsapp_btn.grid(row=0, column=2, padx=10)
        
        # Load initial data
        self.load_services_and_packages()
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def admin_login(self):
        """Handle admin login"""
        if self.is_admin_logged_in:
            self.show_admin_panel()
            return
        
        password = simpledialog.askstring("Admin Login", "Enter admin password:", show='*')
        if password:
            stored_password = self.db.get_admin_setting('admin_password')
            if password == stored_password:
                self.is_admin_logged_in = True
                messagebox.showinfo("Success", "Admin login successful!")
                self.show_admin_panel()
            else:
                messagebox.showerror("Error", "Invalid password!")
    
    def show_admin_panel(self):
        """Show admin management panel"""
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel - SewaSathi")
        admin_window.geometry("600x500")
        admin_window.configure(bg='#f0f8f0')
        
        # Title
        title_label = tk.Label(admin_window, text="🔧 Admin Panel", 
                              font=('Arial', 18, 'bold'), 
                              fg='#2E7D32', bg='#f0f8f0')
        title_label.pack(pady=10)
        
        # Notebook for tabs
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Services tab
        services_frame = ttk.Frame(notebook)
        notebook.add(services_frame, text="Manage Services")
        
        # Add service section
        add_service_frame = ttk.LabelFrame(services_frame, text="Add New Service", padding="10")
        add_service_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(add_service_frame, text="Service Name:").grid(row=0, column=0, sticky=tk.W)
        service_name_entry = tk.Entry(add_service_frame, width=30)
        service_name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(add_service_frame, text="Description:").grid(row=1, column=0, sticky=tk.W)
        service_desc_entry = tk.Entry(add_service_frame, width=30)
        service_desc_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(add_service_frame, text="Base Rate (₹):").grid(row=2, column=0, sticky=tk.W)
        service_rate_entry = tk.Entry(add_service_frame, width=30)
        service_rate_entry.grid(row=2, column=1, padx=5)
        
        def add_service():
            name = service_name_entry.get()
            desc = service_desc_entry.get()
            try:
                rate = float(service_rate_entry.get())
                if self.db.add_service(name, desc, rate):
                    messagebox.showinfo("Success", "Service added successfully!")
                    service_name_entry.delete(0, tk.END)
                    service_desc_entry.delete(0, tk.END)
                    service_rate_entry.delete(0, tk.END)
                    self.load_services_and_packages()
                else:
                    messagebox.showerror("Error", "Service already exists!")
            except ValueError:
                messagebox.showerror("Error", "Invalid rate value!")
        
        ttk.Button(add_service_frame, text="Add Service", command=add_service).grid(row=3, column=1, pady=10)
        
        # Packages tab
        packages_frame = ttk.Frame(notebook)
        notebook.add(packages_frame, text="Manage Packages")
        
        # Add package section
        add_package_frame = ttk.LabelFrame(packages_frame, text="Add New Package", padding="10")
        add_package_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(add_package_frame, text="Package Name:").grid(row=0, column=0, sticky=tk.W)
        package_name_entry = tk.Entry(add_package_frame, width=30)
        package_name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(add_package_frame, text="Multiplier:").grid(row=1, column=0, sticky=tk.W)
        package_mult_entry = tk.Entry(add_package_frame, width=30)
        package_mult_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(add_package_frame, text="Description:").grid(row=2, column=0, sticky=tk.W)
        package_desc_entry = tk.Entry(add_package_frame, width=30)
        package_desc_entry.grid(row=2, column=1, padx=5)
        
        def add_package():
            name = package_name_entry.get()
            desc = package_desc_entry.get()
            try:
                mult = float(package_mult_entry.get())
                if self.db.add_package(name, mult, desc):
                    messagebox.showinfo("Success", "Package added successfully!")
                    package_name_entry.delete(0, tk.END)
                    package_mult_entry.delete(0, tk.END)
                    package_desc_entry.delete(0, tk.END)
                    self.load_services_and_packages()
                else:
                    messagebox.showerror("Error", "Package already exists!")
            except ValueError:
                messagebox.showerror("Error", "Invalid multiplier value!")
        
        ttk.Button(add_package_frame, text="Add Package", command=add_package).grid(row=3, column=1, pady=10)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Tax rate setting
        tax_frame = ttk.LabelFrame(settings_frame, text="Tax Settings", padding="10")
        tax_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(tax_frame, text="Default Tax Rate (%):").grid(row=0, column=0, sticky=tk.W)
        tax_rate_entry = tk.Entry(tax_frame, width=20)
        tax_rate_entry.grid(row=0, column=1, padx=5)
        
        current_tax = self.db.get_admin_setting('tax_rate') or '18.0'
        tax_rate_entry.insert(0, current_tax)
        
        def update_tax_rate():
            try:
                rate = float(tax_rate_entry.get())
                self.db.set_admin_setting('tax_rate', str(rate))
                self.billing_fields['tax_rate'].delete(0, tk.END)
                self.billing_fields['tax_rate'].insert(0, str(rate))
                messagebox.showinfo("Success", "Tax rate updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid tax rate value!")
        
        ttk.Button(tax_frame, text="Update Tax Rate", command=update_tax_rate).grid(row=1, column=1, pady=10)
        
        # Password change
        password_frame = ttk.LabelFrame(settings_frame, text="Change Admin Password", padding="10")
        password_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(password_frame, text="New Password:").grid(row=0, column=0, sticky=tk.W)
        new_password_entry = tk.Entry(password_frame, width=20, show='*')
        new_password_entry.grid(row=0, column=1, padx=5)
        
        def change_password():
            new_password = new_password_entry.get()
            if new_password:
                self.db.set_admin_setting('admin_password', new_password)
                messagebox.showinfo("Success", "Password changed successfully!")
                new_password_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Password cannot be empty!")
        
        ttk.Button(password_frame, text="Change Password", command=change_password).grid(row=1, column=1, pady=10)
    
    def load_services_and_packages(self):
        """Load services and packages from database"""
        # Load services
        services = self.db.get_services()
        service_names = [service[0] for service in services]
        self.service_combo['values'] = service_names
        
        # Load packages
        packages = self.db.get_packages()
        package_names = [package[0] for package in packages]
        self.package_combo['values'] = package_names
        
        # Store rates for calculation
        self.service_rates = {service[0]: service[1] for service in services}
        self.package_multipliers = {package[0]: package[1] for package in packages}
    
    def parse_message(self):
        """Parse WhatsApp message and fill form"""
        message = self.message_text.get("1.0", tk.END)
        if not message.strip():
            messagebox.showwarning("Warning", "Please enter a WhatsApp message to parse!")
            return
        
        booking_data = self.parser.parse_booking_message(message)
        
        # Fill customer fields
        field_mapping = {
            'booking_id': 'booking_id',
            'name': 'customer_name',
            'phone': 'customer_phone',
            'email': 'customer_email',
            'address': 'customer_address',
            'requirements': 'requirements'
        }
        
        for parsed_field, form_field in field_mapping.items():
            if parsed_field in booking_data and form_field in self.customer_fields:
                self.customer_fields[form_field].delete(0, tk.END)
                self.customer_fields[form_field].insert(0, booking_data[parsed_field])
        
        # Fill service fields
        if booking_data.get('service'):
            self.service_var.set(booking_data['service'])
            self.update_service_rate()
        
        if booking_data.get('package'):
            self.package_var.set(booking_data['package'])
        
        if booking_data.get('date'):
            self.service_date.delete(0, tk.END)
            self.service_date.insert(0, booking_data['date'])
        
        if booking_data.get('time'):
            self.service_time.delete(0, tk.END)
            self.service_time.insert(0, booking_data['time'])
        
        self.calculate_total()
        messagebox.showinfo("Success", "Message parsed successfully!")
    
    def clear_message(self):
        """Clear all form fields"""
        self.message_text.delete("1.0", tk.END)
        
        for field in self.customer_fields.values():
            field.delete(0, tk.END)
        
        for field in self.billing_fields.values():
            field.delete(0, tk.END)
        
        self.service_var.set("")
        self.package_var.set("")
        self.service_date.delete(0, tk.END)
        self.service_time.delete(0, tk.END)
        
        # Reset default tax rate
        tax_rate = self.db.get_admin_setting('tax_rate') or '18.0'
        self.billing_fields['tax_rate'].insert(0, tax_rate)
    
    def update_service_rate(self, event=None):
        """Update base amount when service is selected"""
        service_name = self.service_var.get()
        if service_name in self.service_rates:
            base_rate = self.service_rates[service_name]
            self.billing_fields['base_amount'].delete(0, tk.END)
            self.billing_fields['base_amount'].insert(0, str(base_rate))
            self.calculate_total()
    
    def calculate_total(self, event=None):
        """Calculate total amount"""
        try:
            base_amount = float(self.billing_fields['base_amount'].get() or 0)
            extra_charges = float(self.billing_fields['extra_charges'].get() or 0)
            discount = float(self.billing_fields['discount'].get() or 0)
            tax_rate = float(self.billing_fields['tax_rate'].get() or 0)
            
            # Apply package multiplier
            package_name = self.package_var.get()
            if package_name in self.package_multipliers:
                multiplier = self.package_multipliers[package_name]
                base_amount *= multiplier
                self.billing_fields['base_amount'].delete(0, tk.END)
                self.billing_fields['base_amount'].insert(0, f"{base_amount:.2f}")
            
            # Calculate tax
            subtotal = base_amount + extra_charges - discount
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            # Update fields
            self.billing_fields['tax_amount'].delete(0, tk.END)
            self.billing_fields['tax_amount'].insert(0, f"{tax_amount:.2f}")
            
            self.billing_fields['total_amount'].delete(0, tk.END)
            self.billing_fields['total_amount'].insert(0, f"{total_amount:.2f}")
            
        except ValueError:
            pass  # Ignore calculation errors during input
    
    def generate_bill(self):
        """Generate PDF bill"""
        # Validate required fields
        required_fields = ['customer_name', 'service_name', 'package_name']
        
        customer_name = self.customer_fields['customer_name'].get()
        service_name = self.service_var.get()
        package_name = self.package_var.get()
        
        if not all([customer_name, service_name, package_name]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        try:
            # Generate bill number
            bill_no = f"SW{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare bill data
            bill_data = {
                'bill_no': bill_no,
                'booking_id': self.customer_fields['booking_id'].get(),
                'customer_name': customer_name,
                'customer_phone': self.customer_fields['customer_phone'].get(),
                'customer_email': self.customer_fields['customer_email'].get(),
                'customer_address': self.customer_fields['customer_address'].get(),
                'service_name': service_name,
                'package_name': package_name,
                'service_date': self.service_date.get(),
                'service_time': self.service_time.get(),
                'base_amount': float(self.billing_fields['base_amount'].get() or 0),
                'extra_charges': float(self.billing_fields['extra_charges'].get() or 0),
                'discount': float(self.billing_fields['discount'].get() or 0),
                'tax_rate': float(self.billing_fields['tax_rate'].get() or 0),
                'tax_amount': float(self.billing_fields['tax_amount'].get() or 0),
                'total_amount': float(self.billing_fields['total_amount'].get() or 0),
                'requirements': self.customer_fields['requirements'].get()
            }
            
            # Generate PDF
            filename = os.path.join(self.bills_dir, f"Bill_{bill_no}.pdf")
            self.pdf_generator.generate_bill(bill_data, filename)
            
            # Save to database
            db_data = (
                bill_data['bill_no'], bill_data['booking_id'], bill_data['customer_name'],
                bill_data['customer_phone'], bill_data['customer_email'], bill_data['customer_address'],
                bill_data['service_name'], bill_data['package_name'], bill_data['service_date'],
                bill_data['service_time'], bill_data['base_amount'], bill_data['extra_charges'],
                bill_data['discount'], bill_data['tax_rate'], bill_data['tax_amount'],
                bill_data['total_amount'], bill_data['requirements']
            )
            
            self.db.save_bill(db_data)
            
            # Store filename for other operations
            self.last_generated_bill = filename
            
            messagebox.showinfo("Success", f"Bill generated successfully!\nSaved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
    
    def print_bill(self):
        """Print the last generated bill"""
        if not hasattr(self, 'last_generated_bill') or not os.path.exists(self.last_generated_bill):
            messagebox.showerror("Error", "No bill to print! Please generate a bill first.")
            return
        
        try:
            # Open PDF with default application (which usually has print option)
            if sys.platform.startswith('win'):
                os.startfile(self.last_generated_bill)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', self.last_generated_bill])
            else:
                subprocess.call(['xdg-open', self.last_generated_bill])
            
            messagebox.showinfo("Info", "Bill opened in default PDF viewer. Use Ctrl+P to print.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open bill: {str(e)}")
    
    def share_whatsapp(self):
        """Share bill via WhatsApp"""
        if not hasattr(self, 'last_generated_bill') or not os.path.exists(self.last_generated_bill):
            messagebox.showerror("Error", "No bill to share! Please generate a bill first.")
            return
        
        customer_phone = self.customer_fields['customer_phone'].get()
        customer_name = self.customer_fields['customer_name'].get()
        
        # Create WhatsApp message
        message = f"Dear {customer_name},\n\n"
        message += "Thank you for choosing SewaSathi! 🌱\n\n"
        message += "Your service bill is ready. Please find the attached invoice.\n\n"
        message += "Payment can be made via UPI: 9628505560-2@ibl\n\n"
        message += "🙏 Thank you for trusting SewaSathi - Har Kaam Ka Saathi!"
        
        # Clean phone number
        if customer_phone:
            phone = re.sub(r'[^\d+]', '', customer_phone)
            if phone.startswith('+91'):
                phone = phone[3:]
            elif phone.startswith('91'):
                phone = phone[2:]
            
            # WhatsApp Web URL
            whatsapp_url = f"https://web.whatsapp.com/send?phone=91{phone}&text={message}"
        else:
            whatsapp_url = f"https://web.whatsapp.com/send?text={message}"
        
        try:
            webbrowser.open(whatsapp_url)
            messagebox.showinfo("Info", "WhatsApp Web opened! Please attach the bill PDF manually.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open WhatsApp: {str(e)}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = SewaSathiGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()