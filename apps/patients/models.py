"""
Patient Management models
Handles patient records, visits, and diagnoses
"""
from django.db import models
from django.conf import settings
import uuid


class Patient(models.Model):
    """Patient master record"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    # Registration Information
    case_number = models.CharField(max_length=50, unique=True, blank=True, null=True, default=None, help_text="Manual case number")
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    first_visit_date = models.DateField(blank=True, null=True, help_text="Date of first visit to hospital")
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    age_years = models.IntegerField(blank=True, null=True, help_text="Age in years (if DOB unknown)")
    age_months = models.IntegerField(blank=True, null=True, help_text="Age in months component")
    age_days = models.IntegerField(blank=True, null=True, help_text="Age in days component")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    # Address Information
    address = models.TextField(help_text="Street address / Locality")
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True, help_text="PIN/ZIP code")
    
    # Medical and Emergency
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    
    # Referral and Notes
    referred_by = models.CharField(max_length=200, blank=True, null=True, help_text="Doctor/person who referred the patient")
    notes = models.TextField(blank=True, null=True, help_text="General remarks/notes about the patient")
    
    # System Fields
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_patients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['phone']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Auto-generate patient ID: PAT-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_patient = Patient.objects.filter(patient_id__startswith=f'PAT-{date_str}').order_by('-patient_id').first()
            if last_patient:
                last_num = int(last_patient.patient_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.patient_id = f'PAT-{date_str}-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return full name including middle name if available"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate age from date_of_birth or return age_years if DOB not available"""
        if self.date_of_birth:
            from django.utils import timezone
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        elif self.age_years is not None:  # Check for None, not falsy (0 is valid age)
            return self.age_years
        return None
    
    @property
    def age_detail(self):
        """Calculate detailed age breakdown (years, months, days) from date_of_birth"""
        if self.date_of_birth:
            from django.utils import timezone
            from datetime import date
            
            today = timezone.now().date()
            birth_date = self.date_of_birth
            
            # Calculate years
            years = today.year - birth_date.year
            
            # Calculate months
            months = today.month - birth_date.month
            
            # Calculate days
            days = today.day - birth_date.day
            
            # Adjust for negative days
            if days < 0:
                months -= 1
                # Get the last day of previous month
                if today.month == 1:
                    last_month = date(today.year - 1, 12, 1)
                else:
                    last_month = date(today.year, today.month - 1, 1)
                # Days in previous month
                next_month = date(last_month.year, last_month.month % 12 + 1, 1) if last_month.month < 12 else date(last_month.year + 1, 1, 1)
                days_in_prev_month = (next_month - last_month).days
                days += days_in_prev_month
            
            # Adjust for negative months
            if months < 0:
                years -= 1
                months += 12
            
            return {
                'years': years,
                'months': months,
                'days': days
            }
        elif self.age_years is not None or self.age_months is not None or self.age_days is not None:
            return {
                'years': self.age_years or 0,
                'months': self.age_months or 0,
                'days': self.age_days or 0
            }
        return None


class Visit(models.Model):
    """Patient visit records"""
    
    VISIT_TYPE_CHOICES = [
        ('OPD', 'Out-Patient'),
        ('IPD', 'In-Patient'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    visit_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, related_name='visits')
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)
    visit_date = models.DateTimeField(auto_now_add=True)
    chief_complaint = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    vital_signs = models.JSONField(blank=True, null=True)  # BP, temp, pulse, etc.
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'visits'
        ordering = ['-visit_date']
    
    def save(self, *args, **kwargs):
        if not self.visit_id:
            # Auto-generate visit ID: VIS-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_visit = Visit.objects.filter(visit_id__startswith=f'VIS-{date_str}').order_by('-visit_id').first()
            if last_visit:
                last_num = int(last_visit.visit_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.visit_id = f'VIS-{date_str}-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.visit_id} - {self.patient.full_name}"


class Diagnosis(models.Model):
    """Diagnosis and prescription records"""
    
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis = models.TextField()
    prescription = models.TextField()
    medicines = models.ManyToManyField('inventory.Medicine', through='DiagnosisMedicine', related_name='diagnoses')
    lab_tests = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'diagnoses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Diagnosis for {self.visit.visit_id}"


class DiagnosisMedicine(models.Model):
    """Through model for Diagnosis-Medicine relationship"""
    
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    medicine = models.ForeignKey('inventory.Medicine', on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'diagnosis_medicines'
    
    def __str__(self):
        return f"{self.medicine.name} - {self.dosage}"
