"""Prescription views"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from .models import Prescription, PrescriptionMedicine
from .serializers import PrescriptionSerializer, PrescriptionMedicineSerializer
from utils.prescription_pdf import generate_prescription_pdf


class PrescriptionViewSet(viewsets.ModelViewSet):
    """Prescription CRUD and PDF generation"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor', 'status', 'consultation_date']
    search_fields = ['prescription_id', 'patient_name', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['consultation_date', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Generate and download prescription PDF"""
        prescription = self.get_object()
        
        try:
            pdf_bytes = generate_prescription_pdf(prescription)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.prescription_id}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def print(self, request, pk=None):
        """Generate prescription PDF for printing (inline display)"""
        prescription = self.get_object()
        
        try:
            pdf_bytes = generate_prescription_pdf(prescription)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="prescription_{prescription.prescription_id}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def html_view(self, request, pk=None):
        """Render prescription as HTML for browser viewing and printing"""
        from django.shortcuts import render
        from django.conf import settings
        
        prescription = self.get_object()
        medicines = prescription.prescription_medicines.all()
        
        context = {
            'prescription': prescription,
            'doctor': prescription.doctor,
            'medicines': medicines,
            'hospital_name': getattr(settings, 'HOSPITAL_NAME', 'City General Hospital'),
            'hospital_address': getattr(settings, 'HOSPITAL_ADDRESS', ''),
            'hospital_phone': getattr(settings, 'HOSPITAL_PHONE', ''),
            'hospital_email': getattr(settings, 'HOSPITAL_EMAIL', ''),
            'hospital_tagline': getattr(settings, 'HOSPITAL_TAGLINE', 'Excellence in Healthcare'),
            'clinic_timings': getattr(settings, 'CLINIC_TIMINGS', ''),
            'clinic_address_hindi': getattr(settings, 'CLINIC_ADDRESS_HINDI', ''),
        }
        
        return render(request, 'prescriptions/prescription_view.html', context)
