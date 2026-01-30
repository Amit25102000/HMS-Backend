"""Doctor URL patterns"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'', views.DoctorViewSet, basename='doctor')
router.register(r'availability', views.DoctorAvailabilityViewSet, basename='availability')

urlpatterns = router.urls
