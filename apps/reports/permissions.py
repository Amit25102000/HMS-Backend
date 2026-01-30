"""Report permissions"""
from rest_framework import permissions


class CanAccessReports(permissions.BasePermission):
    """
    Custom permission for Reports
    Allows access to ADMIN, DOCTOR, and STAFF roles
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access reports"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow ADMIN, DOCTOR, and STAFF roles
        allowed_roles = ['ADMIN', 'DOCTOR', 'STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']
        user_role = request.user.role.upper()
        
        return user_role in allowed_roles
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific report"""
        user_role = request.user.role.upper()
        
        # ADMIN and STAFF can access all reports
        if user_role in ['ADMIN', 'STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']:
            return True
        
        # DOCTOR can only access their own reports
        if user_role == 'DOCTOR':
            return obj.doctor.user == request.user
        
        return False
