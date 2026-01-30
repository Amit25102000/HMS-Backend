"""
Inventory & Pharmacy Management models
Handles medicines, stock, suppliers, and purchases
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Supplier(models.Model):
    """Medicine suppliers"""
    
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Medicine(models.Model):
    """Medicine master data"""
    
    CATEGORY_CHOICES = [
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('SYRUP', 'Syrup'),
        ('INJECTION', 'Injection'),
        ('CREAM', 'Cream/Ointment'),
        ('DROPS', 'Drops'),
        ('OTHER', 'Other'),
    ]
    
    medicine_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, blank=True, null=True)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])  # Purchase price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medicines'
        ordering = ['name']
        indexes = [
            models.Index(fields=['medicine_id']),
            models.Index(fields=['name']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.medicine_id:
            # Auto-generate medicine ID: MED-XXXX
            last_med = Medicine.objects.order_by('-medicine_id').first()
            if last_med and last_med.medicine_id.startswith('MED-'):
                last_num = int(last_med.medicine_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.medicine_id = f'MED-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.medicine_id} - {self.name}"
    
    @property
    def current_stock(self):
        """Calculate current stock from all batches"""
        return sum(batch.quantity for batch in self.batches.filter(expiry_date__gte=models.functions.Now()))
    
    @property
    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.stock_quantity <= self.reorder_level
    
    @property
    def is_expired(self):
        """Check if any batch is expired"""
        from django.utils import timezone
        return self.batches.filter(expiry_date__lt=timezone.now().date()).exists()
    
    @property
    def status(self):
        """Get medicine status: EXPIRED, LOW_STOCK, or IN_STOCK"""
        if self.is_expired:
            return 'EXPIRED'
        elif self.is_low_stock:
            return 'LOW_STOCK'
        else:
            return 'IN_STOCK'


class MedicineBatch(models.Model):
    """Medicine batch tracking"""
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='batches')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medicine_batches'
        unique_together = ['medicine', 'batch_number']
        ordering = ['expiry_date']
    
    def __str__(self):
        return f"{self.medicine.name} - Batch {self.batch_number}"


class StockTransaction(models.Model):
    """Stock in/out transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('EXPIRED', 'Expired'),
        ('DAMAGED', 'Damaged'),
    ]
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='transactions')
    batch = models.ForeignKey(MedicineBatch, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reference_id = models.CharField(max_length=50, blank=True, null=True)  # invoice/purchase ID
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.medicine.name} ({self.quantity})"


class Purchase(models.Model):
    """Purchase orders"""
    
    purchase_id = models.CharField(max_length=20, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('PENDING', 'Pending'), ('PARTIAL', 'Partial')], default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchases'
        ordering = ['-purchase_date']
    
    def save(self, *args, **kwargs):
        if not self.purchase_id:
            # Auto-generate purchase ID: PUR-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_pur = Purchase.objects.filter(purchase_id__startswith=f'PUR-{date_str}').order_by('-purchase_id').first()
            if last_pur:
                last_num = int(last_pur.purchase_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.purchase_id = f'PUR-{date_str}-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.purchase_id} - {self.supplier.name}"
