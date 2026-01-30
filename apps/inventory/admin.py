from django.contrib import admin
from .models import Supplier, Medicine, MedicineBatch, StockTransaction, Purchase


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'is_active']
    search_fields = ['name', 'contact_person']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_id', 'name', 'category', 'manufacturer', 'unit_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['medicine_id', 'name', 'generic_name']
    readonly_fields = ['medicine_id']


@admin.register(MedicineBatch)
class MedicineBatchAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch_number', 'quantity', 'expiry_date', 'supplier']
    list_filter = ['expiry_date']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'transaction_type', 'quantity', 'created_by', 'created_at']
    list_filter = ['transaction_type', 'created_at']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['purchase_id', 'supplier', 'purchase_date', 'total_amount', 'payment_status']
    list_filter = ['payment_status', 'purchase_date']
    readonly_fields = ['purchase_id']
