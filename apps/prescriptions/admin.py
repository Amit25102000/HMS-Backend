"""Prescription admin"""
from django.contrib import admin
from .models import Prescription, PrescriptionMedicine


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1
    fields = ['medicine', 'dosage', 'frequency', 'duration', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient_name', 'patient_age', 'consultation_date', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'consultation_date', 'created_at']
    search_fields = ['prescription_id', 'patient_name', 'doctor__user__first_name', 'doctor__user__last_name']
    readonly_fields = ['prescription_id', 'total_amount', 'created_by', 'created_at', 'updated_at']
    inlines = [PrescriptionMedicineInline]
    
    fieldsets = (
        ('Prescription Info', {
            'fields': ('prescription_id', 'status', 'total_amount')
        }),
        ('Patient Information', {
            'fields': ('patient', 'patient_name', 'patient_age', 'patient_gender', 'patient_address')
        }),
        ('Doctor and Date', {
            'fields': ('doctor', 'consultation_date')
        }),
        ('Medical Sections', {
            'fields': ('complaint', 'on_examination', 'provisional_diagnosis', 'investigations', 'rx_notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
