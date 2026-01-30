from django.contrib import admin
from .models import Department, Doctor, DoctorAvailability


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_of_department', 'is_active']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'user', 'specialization', 'department', 'consultation_fee', 'is_available']
    list_filter = ['department', 'specialization', 'is_available']
    readonly_fields = ['doctor_id', 'created_at', 'updated_at']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
