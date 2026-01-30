"""
Authentication models for Hospital Management System
Implements custom User model with role-based access control
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model with role-based access control
    Roles: Admin, Doctor, Staff, Receptionist, Pharmacist, Accountant
    """
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('STAFF', 'Staff'),  # General staff role
        ('RECEPTIONIST', 'Receptionist'),
        ('PHARMACIST', 'Pharmacist'),
        ('ACCOUNTANT', 'Accountant'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
    
    @property
    def is_staff_role(self):
        """Check if user is any staff type"""
        return self.role in ['STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']
    
    @property
    def is_receptionist(self):
        return self.role == 'RECEPTIONIST'
    
    @property
    def is_pharmacist(self):
        return self.role == 'PHARMACIST'
    
    @property
    def is_accountant(self):
        return self.role == 'ACCOUNTANT'

