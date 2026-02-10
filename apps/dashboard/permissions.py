"""
Custom permissions for role-based dashboard access
Re-exports permission classes from authentication app for convenience
"""
from apps.authentication.permissions import (
    IsSuperAdminUser,
    IsAdminUser,
    IsDoctorUser,
    IsStaffUser,
    IsDoctorOrStaff,
    IsReceptionistUser,
    IsPharmacistUser
)


# Backward compatibility aliases
class IsDoctorOrAdmin(IsAdminUser):
    """Alias for backward compatibility - Admin permission includes doctors in this context"""
    pass

