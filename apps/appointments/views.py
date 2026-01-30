"""Appointment views"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient', 'doctor__user').all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor', 'status', 'appointment_date']
    ordering_fields = ['appointment_date', 'appointment_time']
    
    def get_queryset(self):
        """Filter appointments based on user role"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Role-based filtering
        user_role = user.role.upper()
        
        if user_role == 'ADMIN':
            # Admin can see all appointments
            return queryset
        elif user_role == 'DOCTOR':
            # Doctor can only see their assigned appointments
            return queryset.filter(doctor__user=user)
        elif user_role in ['STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']:
            # Staff can see all appointments
            return queryset
        
        # Default: no appointments
        return queryset.none()
    
    def list(self, request, *args, **kwargs):
        """Return dummy data if DUMMY_DATA is enabled"""
        if settings.DUMMY_DATA:
            from apps.dashboard.dummy_data import dummy_service
            appointments = dummy_service.get_appointment_list(limit=50)
            
            # Apply role-based filtering to dummy data
            user_role = request.user.role.upper()
            if user_role == 'DOCTOR':
                # Filter to show only some appointments for doctor (simulate assigned)
                appointments = [apt for apt in appointments if apt['id'] % 3 != 0][:15]
            
            return Response(appointments)
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """Update appointment status"""
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = dict(Appointment.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            appointment.status = new_status
            appointment.save()
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid status. Must be one of: ' + ', '.join(valid_statuses)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Confirm appointment"""
        appointment = self.get_object()
        appointment.status = 'CONFIRMED'
        appointment.save()
        return Response({'message': 'Appointment confirmed'})
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel appointment"""
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()
        return Response({'message': 'Appointment cancelled'})
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        appointment.status = 'COMPLETED'
        appointment.save()
        return Response({'message': 'Appointment completed'})
