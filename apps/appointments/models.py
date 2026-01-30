"""
Appointment Management models
Handles appointment booking and scheduling
"""
from django.db import models
from apps.patients.models import Patient
from apps.doctors.models import Doctor


class Appointment(models.Model):
    """Appointment booking system"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    appointment_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Auto-generate appointment ID: APT-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_apt = Appointment.objects.filter(appointment_id__startswith=f'APT-{date_str}').order_by('-appointment_id').first()
            if last_apt:
                last_num = int(last_apt.appointment_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.appointment_id = f'APT-{date_str}-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name} with Dr. {self.doctor.user.get_full_name()}"
