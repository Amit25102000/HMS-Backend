from django.contrib import admin
from .models import Patient, Visit, Diagnosis, DiagnosisMedicine


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'phone', 'gender', 'age', 'is_active']
    list_filter = ['gender', 'blood_group', 'is_active']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['visit_id', 'patient', 'doctor', 'visit_type', 'visit_date', 'is_completed']
    list_filter = ['visit_type', 'is_completed', 'visit_date']
    readonly_fields = ['visit_id', 'created_at', 'updated_at']


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['visit', 'diagnosis', 'follow_up_date']
    list_filter = ['follow_up_date']


admin.site.register(DiagnosisMedicine)
