"""
Custom permissions for role-based dashboard access
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for Admin role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role.upper() == 'ADMIN'


class IsDoctorUser(permissions.BasePermission):
    """
    Permission check for Doctor role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role.upper() == 'DOCTOR'


class IsStaffUser(permissions.BasePermission):
    """
    Permission check for Staff/Receptionist role (any staff type)
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        # Accept STAFF, RECEPTIONIST, PHARMACIST, ACCOUNTANT
        return request.user.role.upper() in ['STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']


class IsDoctorOrStaff(permissions.BasePermission):
    """
    Permission check for Doctor OR Staff roles (for reports, etc.)
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role.upper() in ['DOCTOR', 'STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']
