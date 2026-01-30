"""
Django management command to create test users
Usage: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for all roles'

    def handle(self, *args, **kwargs):
        users_to_create = [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'ADMIN',
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@hospital.com'
            },
            {
                'username': 'doctor',
                'password': 'doctor123',
                'role': 'DOCTOR',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'doctor@hospital.com'
            },
            {
                'username': 'staff',
                'password': 'staff123',
                'role': 'STAFF',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'staff@hospital.com'
            },
        ]

        for user_data in users_to_create:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists, skipping...')
                )
                continue
            
            # Create user using create_user (sets password correctly)
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                role=user_data['role']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created user: {username} ({user_data["role"]})')
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Test users created successfully!\n'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Doctor: doctor / doctor123')
        self.stdout.write('  Staff: staff / staff123')
