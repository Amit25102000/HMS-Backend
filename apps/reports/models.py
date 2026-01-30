"""
Report Management models
Handles medical reports and diagnostic results
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.patients.models import Patient
from apps.doctors.models import Doctor


def report_file_path(instance, filename):
    """Generate file path for report PDFs"""
    return f'reports/{instance.report_type}/{filename}'


class Report(models.Model):
    """Medical Report model"""
    
    REPORT_TYPE_CHOICES = [
        ('BLOOD_TEST', 'Blood Test'),
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI Scan'),
        ('CT_SCAN', 'CT Scan'),
        ('ULTRASOUND', 'Ultrasound'),
        ('ECG', 'ECG'),
        ('PATHOLOGY', 'Pathology'),
        ('RADIOLOGY', 'Radiology'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed'),
    ]
    
    report_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    report_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    findings = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to=report_file_path, 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Upload report file (PDF only, max 10MB)'
    )
    file_size = models.IntegerField(blank=True, null=True, help_text='File size in bytes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_date', 'status']),
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            # Auto-generate report ID: REP-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_report = Report.objects.filter(report_id__startswith=f'REP-{date_str}').order_by('-report_id').first()
            if last_report:
                last_num = int(last_report.report_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.report_id = f'REP-{date_str}-{new_num:04d}'
        
        # Store file size if file exists
        if self.file:
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.report_id} - {self.patient.full_name} - {self.get_report_type_display()}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
