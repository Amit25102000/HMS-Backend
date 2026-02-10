"""
Prescription PDF Generation for Clinic Module
Generates prescription PDFs with specific clinic layout requirements
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO
from django.conf import settings
from datetime import datetime


class PrescriptionPDFCanvas(canvas.Canvas):
    """Custom canvas to add watermark"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
    
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_watermark()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_watermark(self):
        """Draw medical symbol watermark in center"""
        self.saveState()
        self.setFont('Helvetica', 120)
        self.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.1))
        # Medical cross symbol
        self.drawCentredString(A4[0]/2, A4[1]/2, '⚕')
        self.restoreState()


def generate_prescription_pdf(prescription):
    """
    Generate professional prescription PDF for clinic
    Layout: Doctor header, patient info, medical sections, medicines, footer
    """
    buffer = BytesIO()
    
    # Create PDF with custom canvas for watermark
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DoctorHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subheader_style = ParagraphStyle(
        'DoctorSubHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        underline=True
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=8,
        leading=12
    )
    
    # ==================== DOCTOR HEADER ====================
    doctor = prescription.doctor
    
    # Use doctor data if available, fallback to settings
    if doctor:
        doctor_name = f"Dr. {doctor.user.get_full_name()}"
        doctor_qual = doctor.qualification
        doctor_reg = doctor.registration_number
        specialization = doctor.specialization
        department = doctor.department.name if doctor.department else ""
    else:
        doctor_name = getattr(settings, 'DOCTOR_NAME', 'Dr. Medical Practitioner')
        doctor_qual = getattr(settings, 'DOCTOR_QUALIFICATION', 'MBBS, MD')
        doctor_reg = getattr(settings, 'DOCTOR_REGISTRATION_NO', 'REG-12345')
        specialization = ""
        department = ""
    
    clinic_address = getattr(settings, 'CLINIC_ADDRESS', 'Clinic Address')
    clinic_timings = getattr(settings, 'CLINIC_TIMINGS', 'Mon-Sat: 9 AM - 6 PM')
    hospital_name = getattr(settings, 'HOSPITAL_NAME', 'City General Hospital')
    
    # Hospital/Clinic Header
    elements.append(Paragraph(f"<b>{hospital_name}</b>", header_style))
    elements.append(Paragraph(clinic_address, subheader_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Doctor info section
    elements.append(Paragraph(f"<b>{doctor_name}</b>", header_style))
    elements.append(Paragraph(doctor_qual, subheader_style))
    if specialization:
        elements.append(Paragraph(f"<i>{specialization}</i>", subheader_style))
    if department:
        elements.append(Paragraph(f"Department of {department}", subheader_style))
    elements.append(Paragraph(f"Reg. No: {doctor_reg}", subheader_style))
    elements.append(Paragraph(clinic_address, subheader_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Horizontal line
    elements.append(Spacer(1, 0.1*cm))
    line_table = Table([['']], colWidths=[17*cm])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#2c3e50'))
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # ==================== PATIENT INFO BOX ====================
    patient_data = [
        [f"<b>Patient Name:</b> {prescription.patient_name}", f"<b>Date:</b> {prescription.consultation_date.strftime('%d-%b-%Y')}"],
        [f"<b>Age:</b> {prescription.patient_age} years", f"<b>Gender:</b> {prescription.get_patient_gender_display()}"],
        [f"<b>Address:</b> {prescription.patient_address}", f"<b>Prescription ID:</b> {prescription.prescription_id}"]
    ]
    
    patient_table_data = []
    for row in patient_data:
        patient_table_data.append([Paragraph(row[0], normal_style), Paragraph(row[1], normal_style)])
    
    patient_table = Table(patient_table_data, colWidths=[9*cm, 8*cm])
    patient_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== MEDICAL SECTIONS ====================
    
    # Complaint
    if prescription.complaint:
        elements.append(Paragraph("<b>Complaint:</b>", section_heading_style))
        elements.append(Paragraph(prescription.complaint, normal_style))
    
    # On Examination
    if prescription.on_examination:
        elements.append(Paragraph("<b>On Examination:</b>", section_heading_style))
        elements.append(Paragraph(prescription.on_examination, normal_style))
    
    # Provisional Diagnosis
    if prescription.provisional_diagnosis:
        elements.append(Paragraph("<b>Provisional Diagnosis:</b>", section_heading_style))
        elements.append(Paragraph(prescription.provisional_diagnosis, normal_style))
    
    # Investigations
    if prescription.investigations:
        elements.append(Paragraph("<b>Investigations:</b>", section_heading_style))
        elements.append(Paragraph(prescription.investigations, normal_style))
    
    # ==================== Rx (MEDICINES) ====================
    elements.append(Paragraph("<b>Rx (Medicines):</b>", section_heading_style))
    elements.append(Spacer(1, 0.2*cm))
    
    # Medicine table
    medicine_data = [['#', 'Medicine Name', 'Dosage', 'Frequency', 'Duration', 'Qty']]
    
    for idx, pm in enumerate(prescription.prescription_medicines.all(), 1):
        medicine_name = f"{pm.medicine.name}"
        if pm.medicine.brand:
            medicine_name += f" ({pm.medicine.brand})"
        
        medicine_data.append([
            str(idx),
            medicine_name,
            pm.dosage,
            pm.frequency,
            pm.duration,
            str(pm.quantity)
        ])
    
    med_table = Table(medicine_data, colWidths=[0.8*cm, 6*cm, 2.5*cm, 2.5*cm, 2*cm, 1.2*cm])
    med_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Body styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(med_table)
    
    # Additional Rx notes
    if prescription.rx_notes:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"<i>Note: {prescription.rx_notes}</i>", normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== DOCTOR SIGNATURE ====================
    elements.append(Spacer(1, 1*cm))
    signature_data = [
        ['', Paragraph(f"<b>{doctor_name}</b>", normal_style)],
        ['', Paragraph(f"{doctor_qual}", normal_style)],
        ['', Paragraph(f"Reg. No: {doctor_reg}", normal_style)]
    ]
    sig_table = Table(signature_data, colWidths=[10*cm, 7*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (1, 0), (1, 0), 1, colors.black),
    ]))
    elements.append(sig_table)
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.5*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    elements.append(Paragraph(f"<b>Clinic Timings:</b> {clinic_timings}", footer_style))
    elements.append(Paragraph("<i>Not for Medico Legal Purpose</i>", footer_style))
    
    # Build PDF with custom canvas for watermark
    doc.build(elements, canvasmaker=PrescriptionPDFCanvas)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
