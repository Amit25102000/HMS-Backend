"""Dashboard views for statistics and analytics"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.conf import settings
from datetime import timedelta
from apps.patients.models import Patient, Visit
from apps.appointments.models import Appointment
from apps.inventory.models import Medicine
from apps.billing.models import Invoice
from apps.doctors.models import Doctor
from .permissions import IsAdminUser, IsDoctorUser, IsStaffUser
from .dummy_data import dummy_service


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Legacy endpoint for backward compatibility
    Get dashboard statistics
    - Daily patients count
    - Revenue summary
    - Inventory status
    - Appointments overview
    """
    today = timezone.now().date()
    
    # Patient statistics
    total_patients = Patient.objects.filter(is_active=True).count()
    today_patients = Visit.objects.filter(visit_date__date=today).count()
    
    # Appointment statistics
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(
        status='PENDING',
        appointment_date__gte=today
    ).count()
    confirmed_appointments = Appointment.objects.filter(
        status='CONFIRMED',
        appointment_date=today
    ).count()
    
    # Revenue statistics
    today_revenue = Invoice.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_start = today.replace(day=1)
    month_revenue = Invoice.objects.filter(
        created_at__date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    pending_payments = Invoice.objects.filter(
        payment_status__in=['UNPAID', 'PARTIAL']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Inventory statistics
    total_medicines = Medicine.objects.filter(is_active=True).count()
    low_stock_count = len([m for m in Medicine.objects.all() if m.is_low_stock])
    
    return Response({
        'patients': {
            'total': total_patients,
            'today': today_patients,
        },
        'appointments': {
            'today_total': today_appointments,
            'pending': pending_appointments,
            'confirmed': confirmed_appointments,
        },
        'revenue': {
            'today': float(today_revenue),
            'month': float(month_revenue),
            'pending_payments': float(pending_payments),
        },
        'inventory': {
            'total_medicines': total_medicines,
            'low_stock_count': low_stock_count,
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    """
    Admin Dashboard API
    Returns comprehensive statistics for admin users
    """
    # Return dummy data if enabled
    if settings.DUMMY_DATA:
        return Response(dummy_service.get_admin_dashboard_data())
    
    today = timezone.now().date()
    
    # Total patients
    total_patients = Patient.objects.filter(is_active=True).count()
    today_patients = Patient.objects.filter(created_at__date=today).count()
    
    # Total doctors
    total_doctors = Doctor.objects.filter(is_available=True).count()
    active_doctors = Doctor.objects.filter(
        is_available=True,
        user__is_active=True
    ).count()
    
    # Appointments today
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(
        status='PENDING',
        appointment_date__gte=today
    ).count()
    confirmed_appointments = Appointment.objects.filter(
        status='CONFIRMED',
        appointment_date=today
    ).count()
    
    # Revenue summary
    today_revenue = Invoice.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_start = today.replace(day=1)
    month_revenue = Invoice.objects.filter(
        created_at__date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    pending_revenue = Invoice.objects.filter(
        payment_status__in=['UNPAID', 'PARTIAL']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Inventory
    total_medicines = Medicine.objects.filter(is_active=True).count()
    low_stock_count = len([m for m in Medicine.objects.all() if m.is_low_stock])
    
    return Response({
        'patients': {
            'total': total_patients,
            'today': today_patients,
        },
        'doctors': {
            'total': total_doctors,
            'active': active_doctors,
        },
        'appointments': {
            'today': today_appointments,
            'pending': pending_appointments,
            'confirmed': confirmed_appointments,
        },
        'revenue': {
            'today': float(today_revenue),
            'month': float(month_revenue),
            'pending': float(pending_revenue),
        },
        'inventory': {
            'total_medicines': total_medicines,
            'low_stock': low_stock_count,
        }
    })


@api_view(['GET'])
@permission_classes([IsDoctorUser])
def doctor_dashboard(request):
    """
    Doctor Dashboard API
    Returns doctor-specific statistics
    """
    # Return dummy data if enabled
    if settings.DUMMY_DATA:
        return Response(dummy_service.get_doctor_dashboard_data())
    
    today = timezone.now().date()
    user = request.user
    
    # Get doctor profile
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        return Response({
            'error': 'Doctor profile not found for this user'
        }, status=404)
    
    # Today's appointments for this doctor
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).count()
    
    confirmed_today = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today,
        status='CONFIRMED'
    ).count()
    
    pending_today = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today,
        status='PENDING'
    ).count()
    
    # Assigned patients (patients who had appointments with this doctor)
    assigned_patients = Appointment.objects.filter(
        doctor=doctor
    ).values('patient').distinct().count()
    
    # Total appointments this month
    month_start = today.replace(day=1)
    month_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=month_start
    ).count()
    
    # Pending reports/prescriptions (appointments completed but no prescription)
    from apps.prescriptions.models import Prescription
    completed_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='COMPLETED'
    )
    
    appointments_with_prescriptions = Prescription.objects.filter(
        appointment__doctor=doctor
    ).values_list('appointment_id', flat=True)
    
    pending_prescriptions = completed_appointments.exclude(
        id__in=appointments_with_prescriptions
    ).count()
    
    return Response({
        'appointments': {
            'today': today_appointments,
            'confirmed': confirmed_today,
            'pending': pending_today,
            'month': month_appointments,
        },
        'patients': {
            'assigned': assigned_patients,
        },
        'prescriptions': {
            'pending': pending_prescriptions,
        }
    })


@api_view(['GET'])
@permission_classes([IsStaffUser])
def staff_dashboard(request):
    """
    Staff/Reception Dashboard API
    Returns staff-specific statistics for patient registration and appointments
    """
    # Return dummy data if enabled
    if settings.DUMMY_DATA:
        return Response(dummy_service.get_staff_dashboard_data())
    
    today = timezone.now().date()
    
    # New patient registrations today
    new_patients_today = Patient.objects.filter(
        created_at__date=today
    ).count()
    
    # Total active patients
    total_patients = Patient.objects.filter(is_active=True).count()
    
    # Appointment queue - today's appointments
    today_total_appointments = Appointment.objects.filter(
        appointment_date=today
    ).count()
    
    pending_appointments = Appointment.objects.filter(
        appointment_date=today,
        status='PENDING'
    ).count()
    
    confirmed_appointments = Appointment.objects.filter(
        appointment_date=today,
        status='CONFIRMED'
    ).count()
    
    completed_appointments = Appointment.objects.filter(
        appointment_date=today,
        status='COMPLETED'
    ).count()
    
    # Billing queue - unpaid/partial invoices
    unpaid_invoices = Invoice.objects.filter(
        payment_status='UNPAID'
    ).count()
    
    partial_invoices = Invoice.objects.filter(
        payment_status='PARTIAL'
    ).count()
    
    total_pending_amount = Invoice.objects.filter(
        payment_status__in=['UNPAID', 'PARTIAL']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Today's revenue
    today_revenue = Invoice.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    return Response({
        'patients': {
            'new_today': new_patients_today,
            'total_active': total_patients,
        },
        'appointments': {
            'today_total': today_total_appointments,
            'pending': pending_appointments,
            'confirmed': confirmed_appointments,
            'completed': completed_appointments,
        },
        'billing': {
            'unpaid_invoices': unpaid_invoices,
            'partial_invoices': partial_invoices,
            'pending_amount': float(total_pending_amount),
            'today_revenue': float(today_revenue),
        }
    })

