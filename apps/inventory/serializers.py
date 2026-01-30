"""Inventory serializers"""
from rest_framework import serializers
from .models import Supplier, Medicine, MedicineBatch, StockTransaction, Purchase


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class MedicineBatchSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = MedicineBatch
        fields = '__all__'


class MedicineSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    batches = MedicineBatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ['medicine_id', 'created_at', 'updated_at']


class SimpleMedicineSerializer(serializers.ModelSerializer):
    """Simplified serializer for medicine autocomplete in prescriptions"""
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Medicine
        fields = ['id', 'medicine_id', 'name', 'brand', 'selling_price', 'stock_quantity', 'status']


class StockTransactionSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class PurchaseSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['purchase_id', 'created_by', 'created_at', 'updated_at']
