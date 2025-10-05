# 🌱 SewaSathi Billing Software

**Professional billing system for SewaSathi services with GUI and auto-setup**

*Har Kaam Ka Saathi – SewaSathi*

## 📋 Overview

SewaSathi Billing Software is a complete professional billing solution designed for service providers who receive bookings through WhatsApp messages. The software automatically parses booking details and generates professional PDF invoices with UPI payment integration.

## ✨ Features

### 🚀 Core Features
- **WhatsApp Message Parser**: Automatically extracts booking details from formatted WhatsApp messages
- **Professional PDF Bills**: Generates branded invoices with company logo and QR codes
- **Admin Panel**: Manage services, packages, and rates
- **Database Storage**: SQLite database for all billing records
- **Auto-Setup**: Automatically installs required dependencies

### 💼 Admin Features
- Add/update service rates and packages
- Manage extra charges and discounts
- Configure tax rates
- Password-protected admin access
- View and manage billing history

### 🧾 Bill Features
- Professional PDF format with company branding
- QR code for UPI payments (9628505560-2@ibl)
- Detailed billing breakdown
- Terms & conditions
- Auto-generated bill numbers
- Date/time stamps

### 📱 Additional Features
- **Generate Bill**: Creates and saves PDF automatically
- **Print Bill**: Opens print dialog
- **Share via WhatsApp**: Opens WhatsApp with bill details
- **Auto Folder Creation**: Organizes bills in "SewaSathi_Bills" folder

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Windows/Linux/macOS with GUI support

### Quick Start
1. Download the `sewasathi_billing.py` file
2. Run the application:
   ```bash
   python sewasathi_billing.py
   ```
3. The software will automatically install required dependencies on first run

### Manual Installation
If you prefer to install dependencies manually:
```bash
pip install -r requirements.txt
python sewasathi_billing.py
```

## 📖 Usage

### 1. Admin Setup
- Click "Admin Login" (default password: `admin123`)
- Add your services and packages
- Configure tax rates and settings
- Change admin password

### 2. Creating Bills
1. **Parse WhatsApp Message**:
   - Copy the booking message from WhatsApp
   - Paste it in the message box
   - Click "Parse Message" to auto-fill details

2. **Manual Entry**:
   - Fill customer details manually
   - Select service and package
   - Add extra charges or discounts if needed

3. **Generate Bill**:
   - Click "Generate Bill" to create PDF
   - Bills are saved in "SewaSathi_Bills" folder

### 3. WhatsApp Message Format
The software expects messages in this format:
```
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎨 Design Theme
- **Colors**: Green, White, Light Blue (eco-friendly theme)
- **Branding**: SewaSathi logo and slogan
- **Professional**: Clean, modern interface

## 💳 Payment Integration
- **UPI ID**: 9628505560-2@ibl
- **QR Code**: Auto-generated for each bill
- **Payment Methods**: UPI, bank transfer

## 📁 File Structure
```
SewaSathi_Bills/          # Generated bills folder
sewasathi.db              # SQLite database
sewasathi_logo.png        # Auto-generated logo
sewasathi_billing.py      # Main application
requirements.txt          # Dependencies
README.md                 # This file
```

## 🔧 Technical Details

### Dependencies
- **tkinter**: GUI framework (built-in with Python)
- **reportlab**: PDF generation
- **qrcode**: QR code generation
- **Pillow**: Image processing
- **sqlite3**: Database (built-in with Python)

### Database Schema
- **services**: Service names and rates
- **packages**: Package types and multipliers
- **bills**: Complete billing records
- **admin_settings**: Configuration settings

## 🚨 Troubleshooting

### Common Issues
1. **"tkinter not found"**: Install Python with tkinter support
2. **"Permission denied"**: Run as administrator on Windows
3. **"Module not found"**: Let the auto-installer run completely

### Support
For technical support or feature requests, please contact the development team.

## 📄 Terms & Conditions
- No Service, No Payment
- No Work, No Payment

## 🙏 Thank You
Thank You for Choosing SewaSathi! We look forward to serving you again.

---

**Version**: 1.0  
**Author**: AI Assistant  
**License**: Proprietary  
**Company**: SewaSathi - Har Kaam Ka Saathi