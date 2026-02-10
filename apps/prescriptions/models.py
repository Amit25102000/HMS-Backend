"""
Prescription Management models
Handles clinic prescriptions with patient info and medical sections
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.inventory.models import Medicine


class Prescription(models.Model):
    """Clinic prescription with comprehensive medical sections"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Auto-generated ID
    prescription_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Patient Information (duplicated for historical record)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    patient_name = models.CharField(max_length=200)
    patient_age = models.IntegerField(validators=[MinValueValidator(0)])
    patient_gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    patient_address = models.TextField()
    patient_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='Patient weight in kg')
    
    # Doctor and Date
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    consultation_date = models.DateField()
    
    # Medical Sections (exact order as required)
    complaint = models.TextField(blank=True, null=True, help_text="Chief complaint")
    on_examination = models.TextField(blank=True, null=True, help_text="Physical examination findings")
    provisional_diagnosis = models.TextField(blank=True, null=True, help_text="Provisional diagnosis")
    investigations = models.TextField(blank=True, null=True, help_text="Recommended investigations")
    rx_notes = models.TextField(blank=True, null=True, help_text="Additional Rx notes")
    
    # Medicines linked via PrescriptionMedicine
    medicines = models.ManyToManyField(Medicine, through='PrescriptionMedicine', related_name='prescriptions')
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prescription_id']),
            models.Index(fields=['consultation_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            # Auto-generate prescription ID: PRX-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_prx = Prescription.objects.filter(prescription_id__startswith=f'PRX-{date_str}').order_by('-prescription_id').first()
            if last_prx:
                last_num = int(last_prx.prescription_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.prescription_id = f'PRX-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.prescription_id} - {self.patient_name}"


class PrescriptionMedicine(models.Model):
    """Through model for Prescription-Medicine relationship with dosage details"""
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='prescription_medicines')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescription_usages')
    
    # Medicine details
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg, 1 tablet")
    frequency = models.CharField(max_length=100, help_text="e.g., 1-0-1, Twice daily")
    duration = models.CharField(max_length=100, help_text="e.g., 5 days, 1 week")
    instructions = models.TextField(blank=True, null=True, help_text="Special instructions")
    
    # Quantity and pricing
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])  # Captured at time of prescription
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prescription_medicines'
        unique_together = ['prescription', 'medicine']
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update prescription total
        self.prescription.total_amount = sum(pm.total_price for pm in self.prescription.prescription_medicines.all())
        self.prescription.save()
    
    def __str__(self):
        return f"{self.medicine.name} - {self.dosage} ({self.frequency})"
