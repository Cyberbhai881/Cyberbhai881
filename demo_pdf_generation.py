#!/usr/bin/env python3
"""
Demo script to show PDF bill generation
Creates a sample bill without GUI
"""

import os
import sys
from datetime import datetime

# Import required libraries
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
from PIL import Image as PILImage, ImageDraw

def create_sample_logo():
    """Create a sample logo"""
    logo_path = "demo_logo.png"
    img = PILImage.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple eco-friendly design
    draw.rectangle([10, 10, 190, 90], outline='green', width=3)
    draw.ellipse([20, 20, 80, 80], fill='lightgreen')
    draw.text((90, 35), "SewaSathi", fill='green')
    draw.text((90, 55), "🌱 Eco Service", fill='darkgreen')
    
    img.save(logo_path)
    return logo_path

def generate_qr_code():
    """Generate QR code for UPI payment"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("upi://pay?pa=9628505560-2@ibl&pn=SewaSathi&cu=INR")
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = "demo_qr.png"
    qr_img.save(qr_path)
    return qr_path

def generate_sample_bill():
    """Generate a sample PDF bill"""
    print("🌱 Generating Sample SewaSathi Bill...")
    
    # Sample bill data
    bill_data = {
        'bill_no': f"SW{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'booking_id': 'ECO849861',
        'customer_name': 'Sandeep Kumar',
        'customer_phone': '+919628505560',
        'customer_email': 'anshpandit5560@gmail.com',
        'customer_address': 'Naka, Raibareli bypass, Shiv nagar colony',
        'service_name': 'Emergency Green Help',
        'package_name': 'Weekly',
        'service_date': '2025-09-28',
        'service_time': '14:03',
        'base_amount': 450.0,  # 500 * 0.9 (weekly discount)
        'extra_charges': 50.0,
        'discount': 0.0,
        'tax_rate': 18.0,
        'tax_amount': 90.0,
        'total_amount': 590.0,
        'requirements': 'Trusted employee and experience'
    }
    
    # Create PDF
    filename = f"Sample_Bill_{bill_data['bill_no']}.pdf"
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
    logo_path = create_sample_logo()
    header_data = [
        [Image(logo_path, width=100, height=50), 
         Paragraph("<b>SewaSathi</b>", title_style)],
        ["", Paragraph("Har Kaam Ka Saathi – SewaSathi", subtitle_style)]
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
        ["Name:", bill_data['customer_name']],
        ["Phone:", bill_data['customer_phone']],
        ["Email:", bill_data['customer_email']],
        ["Address:", bill_data['customer_address']],
        ["Booking ID:", bill_data['booking_id']],
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
        [bill_data['service_name'], 
         bill_data['package_name'],
         bill_data['service_date'],
         bill_data['service_time']]
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
        ["Base Service Charge", f"₹{bill_data['base_amount']:.2f}"],
        ["Extra Charges", f"₹{bill_data['extra_charges']:.2f}"],
        ["Discount", f"-₹{bill_data['discount']:.2f}"],
        ["Tax Amount (18%)", f"₹{bill_data['tax_amount']:.2f}"],
        ["Total Amount", f"₹{bill_data['total_amount']:.2f}"]
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
    qr_path = generate_qr_code()
    payment_data = [
        ["Payment via UPI", ""],
        [Image(qr_path, width=100, height=100), 
         "UPI ID: 9628505560-2@ibl\n\nScan QR code to pay\nusing any UPI app"]
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
    for temp_file in [logo_path, qr_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print(f"✓ Sample bill generated: {filename}")
    print(f"✓ Bill amount: ₹{bill_data['total_amount']}")
    print(f"✓ Customer: {bill_data['customer_name']}")
    print(f"✓ Service: {bill_data['service_name']} ({bill_data['package_name']})")
    
    return filename

if __name__ == "__main__":
    try:
        bill_file = generate_sample_bill()
        print(f"\n🎉 Demo completed successfully!")
        print(f"📄 Sample bill saved as: {bill_file}")
        print("\nThis demonstrates the PDF generation capability of SewaSathi Billing Software.")
    except Exception as e:
        print(f"❌ Error generating sample bill: {e}")
        sys.exit(1)