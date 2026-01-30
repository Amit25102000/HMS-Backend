"""Appointment serializers"""
from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Check if appointment slot is available"""
        if self.instance is None:  # Creating new appointment
            existing = Appointment.objects.filter(
                doctor=data['doctor'],
                appointment_date=data['appointment_date'],
                appointment_time=data['appointment_time'],
                status__in=['PENDING', 'CONFIRMED']
            ).exists()
            
            if existing:
                raise serializers.ValidationError("This time slot is already booked")
        return data
