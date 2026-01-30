"""
Patient views
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient, Visit, Diagnosis
from .serializers import PatientSerializer, VisitSerializer, DiagnosisSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'blood_group', 'is_active']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['created_at', 'first_name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def visits(self, request, pk=None):
        """Get all visits for a patient"""
        patient = self.get_object()
        visits = patient.visits.all()
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def diagnoses(self, request, pk=None):
        """Get all diagnoses for a patient"""
        patient = self.get_object()
        diagnoses = Diagnosis.objects.filter(visit__patient=patient)
        serializer = DiagnosisSerializer(diagnoses, many=True)
        return Response(serializer.data)


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor', 'visit_type', 'is_completed']
    ordering_fields = ['visit_date']


class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['visit']
