from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'patient', 'invoice_type', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['invoice_type', 'payment_status', 'created_at']
    readonly_fields = ['invoice_id', 'tax_amount', 'discount_amount', 'total_amount', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'invoice', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    readonly_fields = ['payment_id', 'created_at']
