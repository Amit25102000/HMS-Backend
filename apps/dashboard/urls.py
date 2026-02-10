"""Dashboard URL patterns"""
from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard-stats'),  # Legacy
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor-dashboard'),
    path('staff/', views.staff_dashboard, name='staff-dashboard'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin-dashboard'),
    path('menu/', views.menu_config, name='menu-config'),
]

