"""Report views"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import Report
from .serializers import ReportSerializer
from .permissions import CanAccessReports


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Report model with role-based access"""
    
    queryset = Report.objects.select_related('patient', 'doctor__user').all()
    serializer_class = ReportSerializer
    permission_classes = [CanAccessReports]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['patient', 'doctor', 'status', 'report_type', 'report_date']
    ordering_fields = ['report_date', 'created_at', 'status']
    search_fields = ['report_id', 'patient__full_name', 'findings']
    
    def get_queryset(self):
        """Filter reports based on user role"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Role-based filtering
        user_role = user.role.upper()
        
        if user_role == 'ADMIN':
            # Admin can see all reports
            return queryset
        elif user_role == 'DOCTOR':
            # Doctor can only see reports assigned to them
            return queryset.filter(doctor__user=user)
        elif user_role in ['STAFF', 'RECEPTIONIST', 'PHARMACIST', 'ACCOUNTANT']:
            # Staff can see all reports
            return queryset
        
        # Default: no reports
        return queryset.none()
    
    def list(self, request, *args, **kwargs):
        """Return dummy data if DUMMY_DATA is enabled"""
        if settings.DUMMY_DATA:
            from apps.dashboard.dummy_data import dummy_service
            reports = dummy_service.get_report_list(limit=50)
            
            # Apply role-based filtering to dummy data
            user_role = request.user.role.upper()
            if user_role == 'DOCTOR':
                # Filter to show only some reports for doctor (simulate assigned)
                reports = [rep for rep in reports if rep['id'] % 2 == 0][:20]
            
            return Response(reports)
        
        return super().list(request, *args, **kwargs)
    
    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """Update report status"""
        report = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = dict(Report.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            report.status = new_status
            report.save()
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid status. Must be one of: ' + ', '.join(valid_statuses)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'], url_path='upload')
    def upload_file(self, request, pk=None):
        """Upload PDF file for a report"""
        report = self.get_object()
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'Only PDF files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if uploaded_file.size > max_size:
            return Response(
                {'error': f'File size exceeds maximum limit of 10MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the file
        report.file = uploaded_file
        report.save()
        
        serializer = self.get_serializer(report)
        return Response({
            'message': 'File uploaded successfully',
            'report': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        """Download PDF file for a report"""
        from django.http import FileResponse, Http404
        
        report = self.get_object()
        
        if not report.file:
            return Response(
                {'error': 'No file available for this report'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            response = FileResponse(report.file.open('rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report.report_id}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Error downloading file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
