"""Billing serializers"""
from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ['total_price']


class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    balance_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_id', 'tax_amount', 'discount_amount', 'total_amount', 
                           'paid_amount', 'payment_status', 'created_by', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_id', read_only=True)
    patient_name = serializers.CharField(source='invoice.patient.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_id', 'received_by', 'created_at']
