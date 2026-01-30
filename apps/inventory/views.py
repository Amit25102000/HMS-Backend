"""Inventory views"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Supplier, Medicine, MedicineBatch, StockTransaction, Purchase
from .serializers import (SupplierSerializer, MedicineSerializer, MedicineBatchSerializer,
                          StockTransactionSerializer, PurchaseSerializer, SimpleMedicineSerializer)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'contact_person']
    filterset_fields = ['is_active']


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['medicine_id', 'name', 'generic_name', 'manufacturer']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get medicines with low stock"""
        low_stock_medicines = [m for m in self.queryset if m.is_low_stock]
        serializer = self.get_serializer(low_stock_medicines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired_medicines(self, request):
        """Get expired medicines"""
        expired_medicines = [m for m in self.queryset if m.is_expired]
        serializer = self.get_serializer(expired_medicines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_autocomplete(self, request):
        """Search medicines for autocomplete in prescription form"""
        query = request.query_params.get('q', '')
        medicines = Medicine.objects.filter(
            name__icontains=query,
            is_active=True,
            stock_quantity__gt=0
        )[:20]
        serializer = SimpleMedicineSerializer(medicines, many=True)
        return Response(serializer.data)


class MedicineBatchViewSet(viewsets.ModelViewSet):
    queryset = MedicineBatch.objects.all()
    serializer_class = MedicineBatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medicine', 'supplier']


class StockTransactionViewSet(viewsets.ModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medicine', 'transaction_type']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['supplier', 'payment_status']
    ordering_fields = ['purchase_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
