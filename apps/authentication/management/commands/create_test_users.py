"""
Django management command to create test users for Hospital Management System
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for development and testing'

    def handle(self, *args, **kwargs):
        # Create SuperAdmin
        if not User.objects.filter(username='superadmin').exists():
            superadmin = User.objects.create_superuser(
                username='superadmin',
                email='superadmin@hospital.com',
                password='super123',
                first_name='Super',
                last_name='Admin',
                role='SUPER_ADMIN'
            )
            admin_group, _ = Group.objects.get_or_create(name='SuperAdmin')
            superadmin.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'✓ Created SuperAdmin: {superadmin.username}'))
        else:
            self.stdout.write(self.style.WARNING('SuperAdmin already exists'))

        # Create Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@hospital.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='ADMIN'
            )
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            admin.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'✓ Created Admin: {admin.username}'))
        else:
            self.stdout.write(self.style.WARNING('Admin already exists'))

        # Create Doctor
        if not User.objects.filter(username='doctor').exists():
            doctor = User.objects.create_user(
                username='doctor',
                email='doctor@hospital.com',
                password='doctor123',
                first_name='Test',
                last_name='Doctor',
                role='DOCTOR'
            )
            doctor_group, _ = Group.objects.get_or_create(name='Doctor')
            doctor.groups.add(doctor_group)
            self.stdout.write(self.style.SUCCESS(f'✓ Created Doctor: {doctor.username}'))
        else:
            self.stdout.write(self.style.WARNING('Doctor already exists'))

        # Create Staff
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user(
                username='staff',
                email='staff@hospital.com',
                password='staff123',
                first_name='Test',
                last_name='Staff',
                role='STAFF'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created Staff: {staff.username}'))
        else:
            self.stdout.write(self.style.WARNING('Staff already exists'))

        self.stdout.write(self.style.SUCCESS('\n--- All Users ---'))
        for user in User.objects.all():
            self.stdout.write(f'  {user.username} - {user.get_role_display()} - Active: {user.is_active}')
