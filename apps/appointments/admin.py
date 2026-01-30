from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    readonly_fields = ['appointment_id', 'created_at', 'updated_at']
    search_fields = ['appointment_id', 'patient__first_name', 'patient__last_name']
