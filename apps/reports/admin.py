"""Admin configuration for Reports"""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model"""
    
    list_display = ['report_id', 'patient', 'doctor', 'report_type', 'status', 'report_date', 'created_at']
    list_filter = ['status', 'report_type', 'report_date']
    search_fields = ['report_id', 'patient__full_name', 'doctor__user__username', 'findings']
    readonly_fields = ['report_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_id', 'patient', 'doctor', 'report_type', 'status')
        }),
        ('Details', {
            'fields': ('report_date', 'findings', 'file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
