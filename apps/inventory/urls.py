"""Inventory URL patterns"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'medicines', views.MedicineViewSet, basename='medicine')
router.register(r'batches', views.MedicineBatchViewSet, basename='batch')
router.register(r'transactions', views.StockTransactionViewSet, basename='transaction')
router.register(r'purchases', views.PurchaseViewSet, basename='purchase')

urlpatterns = router.urls
