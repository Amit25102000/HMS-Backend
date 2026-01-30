"""
Patient serializers
"""
from rest_framework import serializers
from .models import Patient, Visit, Diagnosis, DiagnosisMedicine


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    age_detail = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'case_number', 'first_name', 'middle_name', 'last_name', 
                  'full_name', 'date_of_birth', 'age_years', 'age_months', 'age_days', 'age', 
                  'age_detail', 'gender', 'blood_group', 'height', 'weight', 'phone', 'email', 
                  'address', 'city', 'state', 'pin_code', 'emergency_contact_name', 'emergency_contact_phone', 
                  'medical_history', 'allergies', 'referred_by', 'first_visit_date', 'notes', 'is_active', 
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['patient_id', 'created_by', 'created_at', 'updated_at', 'age', 
                           'age_detail', 'full_name']


class VisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    
    class Meta:
        model = Visit
        fields = '__all__'
        read_only_fields = ['visit_id', 'created_at', 'updated_at']


class DiagnosisMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    
    class Meta:
        model = DiagnosisMedicine
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    medicines_detail = DiagnosisMedicineSerializer(source='diagnosismedicine_set', many=True, read_only=True)
    
    class Meta:
        model = Diagnosis
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
