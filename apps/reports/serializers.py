"""Report serializers"""
from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField(read_only=True)
    has_file = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id',
            'report_id',
            'patient',
            'patient_name',
            'patient_id',
            'patient_phone',
            'doctor',
            'doctor_name',
            'report_type',
            'report_type_display',
            'report_date',
            'status',
            'status_display',
            'findings',
            'file',
            'file_size',
            'file_size_mb',
            'has_file',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at', 'report_date', 'file_size']
    
    def get_doctor_name(self, obj):
        """Get formatted doctor name"""
        if obj.doctor and obj.doctor.user:
            return f"Dr. {obj.doctor.user.get_full_name() or obj.doctor.user.username}"
        return "Unknown"
    
    def get_file_size_mb(self, obj):
        """Get file size in MB"""
        return obj.file_size_mb
    
    def get_has_file(self, obj):
        """Check if report has a file attached"""
        return bool(obj.file)
