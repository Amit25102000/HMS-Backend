"""Prescription serializers"""
from rest_framework import serializers
from .models import Prescription, PrescriptionMedicine
from apps.inventory.models import Medicine


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_brand = serializers.CharField(source='medicine.brand', read_only=True)
    available_stock = serializers.IntegerField(source='medicine.stock_quantity', read_only=True)
    
    class Meta:
        model = PrescriptionMedicine
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_brand', 
            'dosage', 'frequency', 'duration', 'instructions',
            'quantity', 'unit_price', 'total_price', 'available_stock'
        ]
        read_only_fields = ['total_price']
    
    def validate(self, data):
        """Validate stock availability"""
        medicine = data.get('medicine')
        quantity = data.get('quantity')
        
        if medicine and quantity:
            if medicine.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Insufficient stock. Available: {medicine.stock_quantity}'
                })
        
        return data


class PrescriptionSerializer(serializers.ModelSerializer):
    prescription_medicines = PrescriptionMedicineSerializer(many=True, required=False)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_full_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'total_amount', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create prescription with medicines"""
        medicines_data = validated_data.pop('prescription_medicines', [])
        prescription = Prescription.objects.create(**validated_data)
        
        for medicine_data in medicines_data:
            PrescriptionMedicine.objects.create(prescription=prescription, **medicine_data)
        
        return prescription
    
    def update(self, instance, validated_data):
        """Update prescription with medicines"""
        medicines_data = validated_data.pop('prescription_medicines', None)
        
        # Update prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update medicines if provided
        if medicines_data is not None:
            # Remove existing medicines
            instance.prescription_medicines.all().delete()
            
            # Add new medicines
            for medicine_data in medicines_data:
                PrescriptionMedicine.objects.create(prescription=instance, **medicine_data)
        
        return instance


class SimpleMedicineSerializer(serializers.ModelSerializer):
    """Simplified serializer for medicine autocomplete"""
    
    class Meta:
        model = Medicine
        fields = ['id', 'medicine_id', 'name', 'brand', 'selling_price', 'stock_quantity', 'status']
