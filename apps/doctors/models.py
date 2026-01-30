"""
Doctor Management models
Handles doctor profiles, departments, and availability
"""
from django.db import models
from django.conf import settings


class Department(models.Model):
    """Medical departments"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    head_of_department = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Doctor profiles"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_id = models.CharField(max_length=20, unique=True, editable=False)
    specialization = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    registration_number = models.CharField(max_length=50, unique=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors'
        ordering = ['user__first_name']
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            # Auto-generate doctor ID: DOC-XXXX
            last_doctor = Doctor.objects.order_by('-doctor_id').first()
            if last_doctor and last_doctor.doctor_id.startswith('DOC-'):
                last_num = int(last_doctor.doctor_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.doctor_id = f'DOC-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"


class DoctorAvailability(models.Model):
    """Doctor schedule and availability"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_appointments = models.IntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'doctor_availability'
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
