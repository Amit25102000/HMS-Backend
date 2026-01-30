"""
PDF Generation utilities using ReportLab
Generates professional PDFs for prescriptions, invoices, and medical documents
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings
from datetime import datetime


def get_hospital_header():
    """Get hospital information for header"""
    return {
        'name': settings.HOSPITAL_NAME,
        'address': settings.HOSPITAL_ADDRESS,
        'phone': settings.HOSPITAL_PHONE,
        'email': settings.HOSPITAL_EMAIL,
    }


def generate_invoice_pdf(invoice):
    """
    Generate professional invoice PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
    )
    
    # Hospital Header
    hospital = get_hospital_header()
    hospital_name = Paragraph(f"<b>{hospital['name']}</b>", title_style)
    elements.append(hospital_name)
    
    hospital_info = Paragraph(
        f"{hospital['address']}<br/>Phone: {hospital['phone']} | Email: {hospital['email']}",
        styles['Normal']
    )
    elements.append(hospital_info)
    elements.append(Spacer(1, 20))
    
    # Invoice Title
    invoice_title = Paragraph(f"<b>INVOICE</b>", heading_style)
    elements.append(invoice_title)
    elements.append(Spacer(1, 10))
    
    # Invoice Details
    invoice_data = [
        ['Invoice Number:', invoice.invoice_id],
        ['Date:', invoice.invoice_date.strftime('%d-%m-%Y %I:%M %p')],
        ['Patient Name:', invoice.patient.full_name],
        ['Patient ID:', invoice.patient.patient_id],
        ['Invoice Type:', invoice.get_invoice_type_display()],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Invoice Items
    items_heading = Paragraph("<b>Items</b>", heading_style)
    elements.append(items_heading)
    
    items_data = [['#', 'Description', 'Qty', 'Unit Price', 'Total']]
    for idx, item in enumerate(invoice.items.all(), 1):
        items_data.append([
            str(idx),
            item.description,
            str(item.quantity),
            f"₹{item.unit_price:.2f}",
            f"₹{item.total_price:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    totals_data = [
        ['Subtotal:', f"₹{invoice.subtotal:.2f}"],
        [f'Tax ({invoice.tax_percentage}%):', f"₹{invoice.tax_amount:.2f}"],
        [f'Discount ({invoice.discount_percentage}%):', f"-₹{invoice.discount_amount:.2f}"],
        ['<b>Total Amount:</b>', f"<b>₹{invoice.total_amount:.2f}</b>"],
        ['Paid Amount:', f"₹{invoice.paid_amount:.2f}"],
        ['<b>Balance Due:</b>', f"<b>₹{invoice.balance_amount:.2f}</b>"],
    ]
    
    totals_table = Table(totals_data, colWidths=[4.5*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.black),
        ('LINEABOVE', (0, 5), (-1, 5), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = Paragraph(
        "<i>Thank you for choosing our hospital. We wish you good health!</i>",
        styles['Italic']
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_prescription_pdf(diagnosis):
    """
    Generate prescription PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Hospital Header
    hospital = get_hospital_header()
    hospital_name = Paragraph(f"<b>{hospital['name']}</b>", styles['Title'])
    elements.append(hospital_name)
    elements.append(Spacer(1, 12))
    
    # Prescription Title
    elements.append(Paragraph("<b>PRESCRIPTION</b>", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    # Patient Details
    visit = diagnosis.visit
    patient = visit.patient
    
    patient_data = [
        ['Patient Name:', patient.full_name, 'Patient ID:', patient.patient_id],
        ['Age:', f"{patient.age} years", 'Gender:', patient.get_gender_display()],
        ['Date:', visit.visit_date.strftime('%d-%m-%Y'), 'Doctor:', visit.doctor.user.get_full_name()],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))
    
    # Diagnosis
    elements.append(Paragraph(f"<b>Diagnosis:</b> {diagnosis.diagnosis}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Medicines
    elements.append(Paragraph("<b>Prescribed Medicines:</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))
    
    med_data = [['Medicine', 'Dosage', 'Frequency', 'Duration']]
    for dm in diagnosis.diagnosismedicine_set.all():
        med_data.append([
            dm.medicine.name,
            dm.dosage,
            dm.frequency,
            dm.duration
        ])
    
    med_table = Table(med_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(med_table)
    elements.append(Spacer(1, 20))
    
    # Instructions
    if diagnosis.notes:
        elements.append(Paragraph(f"<b>Instructions:</b> {diagnosis.notes}", styles['Normal']))
    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
