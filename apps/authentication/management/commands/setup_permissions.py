"""
Django management command to setup role-based permissions
Creates Groups and assigns permissions for each role
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.authentication.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor, Department
from apps.appointments.models import Appointment
from apps.prescriptions.models import Prescription
from apps.inventory.models import Medicine
from apps.billing.models import Invoice


class Command(BaseCommand):
    help = 'Setup role-based permissions and groups'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Setting up permissions and groups...'))

        # Define role permissions mapping
        role_permissions = {
            'SuperAdmin': {
                'description': 'Complete system access',
                'models': ['*'],  # All permissions
                'permissions': ['add', 'change', 'delete', 'view']
            },
            'Admin': {
                'description': 'Administrative access',
                'models': [User, Patient, Doctor, Department, Appointment, Prescription, Medicine, Invoice],
                'permissions': ['add', 'change', 'delete', 'view']
            },
            'Doctor': {
                'description': 'Doctor access',
                'models': {
                    Patient: ['view'],
                    Appointment: ['view', 'change'],
                    Prescription: ['add', 'change', 'view', 'delete'],
                    Medicine: ['view'],
                    Doctor: ['view', 'change'],  # Can update own profile
                }
            },
            'Receptionist': {
                'description': 'Reception desk access',
                'models': {
                    Patient: ['add', 'change', 'view'],
                    Appointment: ['add', 'change', 'view', 'delete'],
                    Doctor: ['view'],
                    Department: ['view'],
                    Invoice: ['view', 'add', 'change'],
                }
            },
            'Pharmacist': {
                'description': 'Pharmacy access',
                'models': {
                    Prescription: ['view'],
                    Medicine: ['add', 'change', 'view', 'delete'],
                    Patient: ['view'],
                    Invoice: ['view'],
                }
            },
            'Accountant': {
                'description': 'Billing and accounting access',
                'models': {
                    Invoice: ['add', 'change', 'view', 'delete'],
                    Patient: ['view'],
                    Appointment: ['view'],
                }
            },
        }

        # Create groups and assign permissions
        for role_name, config in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            else:
                self.stdout.write(f'Group already exists: {role_name}')
                # Clear existing permissions
                group.permissions.clear()

            # Handle SuperAdmin special case
            if role_name == 'SuperAdmin':
                # Grant all permissions
                all_permissions = Permission.objects.all()
                group.permissions.set(all_permissions)
                self.stdout.write(self.style.SUCCESS(f'  → Granted ALL permissions to {role_name}'))
                continue

            # Handle Admin
            if role_name == 'Admin':
                models = config['models']
                for model in models:
                    content_type = ContentType.objects.get_for_model(model)
                    permissions = Permission.objects.filter(content_type=content_type)
                    group.permissions.add(*permissions)
                    self.stdout.write(f'  → Added all permissions for {model.__name__}')
                continue

            # Handle other roles with specific permissions
            models = config['models']
            for model, perms in models.items():
                content_type = ContentType.objects.get_for_model(model)
                for perm in perms:
                    codename = f'{perm}_{model._meta.model_name}'
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        group.permissions.add(permission)
                        self.stdout.write(f'  → Added {perm} permission for {model.__name__}')
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ Permission not found: {codename}')
                        )

        self.stdout.write(self.style.SUCCESS('\n✓ Permissions setup completed!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Assign users to groups using Django admin or shell')
        self.stdout.write('2. Users will inherit permissions from their assigned group')
        self.stdout.write('\nExample: ')
        self.stdout.write('  user = User.objects.get(username="doctor1")')
        self.stdout.write('  group = Group.objects.get(name="Doctor")')
        self.stdout.write('  user.groups.add(group)')
