"""Billing URL patterns"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'invoice-items', views.InvoiceItemViewSet, basename='invoice-item')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = router.urls
