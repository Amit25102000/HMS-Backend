"""Doctor views"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Doctor, DoctorAvailability
from .serializers import DepartmentSerializer, DoctorSerializer, DoctorAvailabilitySerializer
import logging

logger = logging.getLogger(__name__)


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
    
    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to add better logging and validation"""
        try:
            instance = self.get_object()
            logger.info(f"Updating doctor {instance.doctor_id}: {request.data}")
            
            # Validate availability toggle
            if 'is_available' in request.data:
                if not isinstance(request.data['is_available'], bool):
                    return Response(
                        {'detail': 'is_available must be a boolean value'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            response = super().partial_update(request, *args, **kwargs)
            logger.info(f"Successfully updated doctor {instance.doctor_id}")
            return response
        except Exception as e:
            logger.error(f"Error updating doctor: {str(e)}", exc_info=True)
            return Response(
                {'detail': f'Failed to update doctor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get doctor availability schedule"""
        try:
            doctor = self.get_object()
            availability = doctor.availability.filter(is_active=True)
            serializer = DoctorAvailabilitySerializer(availability, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching doctor availability: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'Failed to fetch doctor availability'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'day_of_week', 'is_active']
