"""
Comprehensive permission classes for role-based access control
Provides granular permission checks for different user roles and operations
"""
from rest_framework import permissions


class IsSuperAdminUser(permissions.BasePermission):
    """
    Permission check for Super Admin role
    Super Admins have complete system access
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'SUPER_ADMIN'
        )


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for Admin role (includes Super Admin)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ADMIN', 'SUPER_ADMIN']
        )


class IsDoctorUser(permissions.BasePermission):
    """
    Permission check for Doctor role
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'DOCTOR'
        )


class IsReceptionistUser(permissions.BasePermission):
    """
    Permission check for Receptionist role
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'RECEPTIONIST'
        )


class IsPharmacistUser(permissions.BasePermission):
    """
    Permission check for Pharmacist role
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'PHARMACIST'
        )


class IsStaffUser(permissions.BasePermission):
    """
    Permission check for any Staff role
    Includes: Staff, Receptionist, Pharmacist, Accountant
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']
        )


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permission check for Doctor OR Admin/SuperAdmin roles
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['DOCTOR', 'ADMIN', 'SUPER_ADMIN']
        )


class IsDoctorOrStaff(permissions.BasePermission):
    """
    Permission check for Doctor OR Staff roles
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['DOCTOR', 'STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners or admins to edit
    Use with has_object_permission
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Super Admin has all access
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # Admin has all access
        if request.user.role == 'ADMIN':
            return True
        
        # Check if object has user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object has created_by field
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class CanViewPatients(permissions.BasePermission):
    """
    Permission to view patient records
    Allowed: SuperAdmin, Admin, Doctor, Receptionist
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'DOCTOR', 'RECEPTIONIST', 'STAFF']
        )


class CanManagePatients(permissions.BasePermission):
    """
    Permission to create/edit patient records
    Allowed: SuperAdmin, Admin, Receptionist
    """
    def has_permission(self, request, view):
        # For read operations, use CanViewPatients
        if request.method in permissions.SAFE_METHODS:
            return CanViewPatients().has_permission(request, view)
        
        # For write operations
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'RECEPTIONIST', 'STAFF']
        )


class CanViewPrescriptions(permissions.BasePermission):
    """
    Permission to view prescriptions
    Allowed: SuperAdmin, Admin, Doctor, Pharmacist
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'DOCTOR', 'PHARMACIST']
        )


class CanManagePrescriptions(permissions.BasePermission):
    """
    Permission to create/edit prescriptions
    Allowed: SuperAdmin, Admin, Doctor
    """
    def has_permission(self, request, view):
        # For read operations, use CanViewPrescriptions
        if request.method in permissions.SAFE_METHODS:
            return CanViewPrescriptions().has_permission(request, view)
        
        # For write operations
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'DOCTOR']
        )


class CanViewInventory(permissions.BasePermission):
    """
    Permission to view inventory/medicines
    Allowed: All authenticated users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanManageInventory(permissions.BasePermission):
    """
    Permission to manage inventory
    Allowed: SuperAdmin, Admin, Pharmacist
    """
    def has_permission(self, request, view):
        # For read operations, all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # For write operations
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'PHARMACIST']
        )


class CanViewBilling(permissions.BasePermission):
    """
    Permission to view billing/invoices
    Allowed: SuperAdmin, Admin, Receptionist, Accountant
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'RECEPTIONIST', 'ACCOUNTANT', 'STAFF']
        )


class CanManageBilling(permissions.BasePermission):
    """
    Permission to create/edit billing records
    Allowed: SuperAdmin, Admin, Receptionist, Accountant
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPER_ADMIN', 'ADMIN', 'RECEPTIONIST', 'ACCOUNTANT', 'STAFF']
        )
