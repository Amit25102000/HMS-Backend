"""Doctor views"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Doctor, DoctorAvailability
from .serializers import DepartmentSerializer, DoctorSerializer, DoctorAvailabilitySerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related('user', 'department').all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get doctor availability schedule"""
        doctor = self.get_object()
        availability = doctor.availability.filter(is_active=True)
        serializer = DoctorAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'day_of_week', 'is_active']
