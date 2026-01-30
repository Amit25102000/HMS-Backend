"""
Billing & Invoicing models
Handles invoices, payments, and billing
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.patients.models import Patient
from apps.inventory.models import Medicine


class Invoice(models.Model):
    """Invoice/Bill management"""
    
    INVOICE_TYPE_CHOICES = [
        ('OPD', 'OPD Consultation'),
        ('IPD', 'IPD Treatment'),
        ('PHARMACY', 'Pharmacy'),
        ('LAB', 'Laboratory'),
        ('OTHER', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]
    
    invoice_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    invoice_date = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_id']),
            models.Index(fields=['payment_status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            # Auto-generate invoice ID: INV-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_inv = Invoice.objects.filter(invoice_id__startswith=f'INV-{date_str}').order_by('-invoice_id').first()
            if last_inv:
                last_num = int(last_inv.invoice_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.invoice_id = f'INV-{date_str}-{new_num:04d}'
        
        # Calculate totals
        self.tax_amount = (self.subtotal * self.tax_percentage) / 100
        self.discount_amount = (self.subtotal * self.discount_percentage) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        # Update payment status
        if self.paid_amount >= self.total_amount:
            self.payment_status = 'PAID'
        elif self.paid_amount > 0:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.invoice_id} - {self.patient.full_name}"
    
    @property
    def balance_amount(self):
        return self.total_amount - self.paid_amount


class InvoiceItem(models.Model):
    """Invoice line items"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'invoice_items'
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} x {self.quantity}"


class Payment(models.Model):
    """Payment records"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('OTHER', 'Other'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Auto-generate payment ID: PAY-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_pay = Payment.objects.filter(payment_id__startswith=f'PAY-{date_str}').order_by('-payment_id').first()
            if last_pay:
                last_num = int(last_pay.payment_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.payment_id = f'PAY-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)
        
        # Update invoice paid amount
        self.invoice.paid_amount = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.save()
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount}"
