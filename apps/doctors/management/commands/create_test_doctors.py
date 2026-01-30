"""
Management command to create test doctor accounts for development/demo
Usage: python manage.py create_test_doctors
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.doctors.models import Doctor, Department

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test doctor accounts with complete profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of doctor accounts to create (default: 15)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.WARNING(f'Creating {count} test doctor accounts...'))
        
        # Create departments if they don't exist
        departments_data = [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
            {'name': 'Neurology', 'description': 'Brain and nervous system'},
            {'name': 'Orthopedics', 'description': 'Bones, joints, and muscles'},
            {'name': 'Pediatrics', 'description': 'Children\'s health'},
            {'name': 'Dermatology', 'description': 'Skin, hair, and nails'},
            {'name': 'Ophthalmology', 'description': 'Eyes and vision'},
            {'name': 'ENT', 'description': 'Ear, Nose, and Throat'},
            {'name': 'General Medicine', 'description': 'General medical care'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            departments.append(dept)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Created department: {dept.name}'))
        
        # Doctor data templates
        doctor_profiles = [
            {'first': 'Anil', 'last': 'Kumar', 'spec': 'Cardiologist', 'qual': 'MBBS, MD (Cardiology)', 'exp': 15, 'dept': 'Cardiology', 'fee': 1500},
            {'first': 'Priya', 'last': 'Sharma', 'spec': 'Neurologist', 'qual': 'MBBS, MD (Neurology)', 'exp': 12, 'dept': 'Neurology', 'fee': 1800},
            {'first': 'Rajesh', 'last': 'Patel', 'spec': 'Orthopedic Surgeon', 'qual': 'MBBS, MS (Orthopedics)', 'exp': 18, 'dept': 'Orthopedics', 'fee': 2000},
            {'first': 'Sneha', 'last': 'Reddy', 'spec': 'Pediatrician', 'qual': 'MBBS, MD (Pediatrics)', 'exp': 10, 'dept': 'Pediatrics', 'fee': 1200},
            {'first': 'Vikram', 'last': 'Singh', 'spec': 'Dermatologist', 'qual': 'MBBS, MD (Dermatology)', 'exp': 8, 'dept': 'Dermatology', 'fee': 1000},
            {'first': 'Kavita', 'last': 'Mehta', 'spec': 'Ophthalmologist', 'qual': 'MBBS, MS (Ophthalmology)', 'exp': 14, 'dept': 'Ophthalmology', 'fee': 1400},
            {'first': 'Arjun', 'last': 'Nair', 'spec': 'ENT Specialist', 'qual': 'MBBS, MS (ENT)', 'exp': 11, 'dept': 'ENT', 'fee': 1300},
            {'first': 'Divya', 'last': 'Iyer', 'spec': 'General Physician', 'qual': 'MBBS, MD (Medicine)', 'exp': 7, 'dept': 'General Medicine', 'fee': 800},
            {'first': 'Suresh', 'last': 'Gupta', 'spec': 'Cardiologist', 'qual': 'MBBS, DM (Cardiology)', 'exp': 20, 'dept': 'Cardiology', 'fee': 2500},
            {'first': 'Anjali', 'last': 'Verma', 'spec': 'Pediatrician', 'qual': 'MBBS, DCH, MD (Pediatrics)', 'exp': 9, 'dept': 'Pediatrics', 'fee': 1100},
            {'first': 'Karthik', 'last': 'Rao', 'spec': 'Neurologist', 'qual': 'MBBS, DM (Neurology)', 'exp': 13, 'dept': 'Neurology', 'fee': 1900},
            {'first': 'Meera', 'last': 'Joshi', 'spec': 'Dermatologist', 'qual': 'MBBS, DVD, MD (Dermatology)', 'exp': 6, 'dept': 'Dermatology', 'fee': 900},
            {'first': 'Rahul', 'last': 'Das', 'spec': 'Orthopedic Surgeon', 'qual': 'MBBS, DNB (Orthopedics)', 'exp': 16, 'dept': 'Orthopedics', 'fee': 1700},
            {'first': 'Pooja', 'last': 'Khanna', 'spec': 'Ophthalmologist', 'qual': 'MBBS, MS (Ophthalmology)', 'exp': 5, 'dept': 'Ophthalmology', 'fee': 850},
            {'first': 'Amit', 'last': 'Desai', 'spec': 'General Physician', 'qual': 'MBBS, MD (General Medicine)', 'exp': 10, 'dept': 'General Medicine', 'fee': 1000},
        ]
        
        created_count = 0
        with transaction.atomic():
            for i, profile in enumerate(doctor_profiles[:count], start=1):
                username = f"doctor{i:03d}"
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f'  [!] User {username} already exists, skipping...'))
                    continue
                
                # Create user account
                user = User.objects.create_user(
                    username=username,
                    email=f"doctor{i}@hospital.com",
                    password="doctor@123",  # Default password for testing
                    first_name=profile['first'],
                    last_name=profile['last'],
                    role='DOCTOR',
                    is_active=True
                )
                
                # Get department
                department = Department.objects.get(name=profile['dept'])
                
                # Create doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    specialization=profile['spec'],
                    department=department,
                    qualification=profile['qual'],
                    experience_years=profile['exp'],
                    registration_number=f"MCI-{2024000 + i}",
                    consultation_fee=profile['fee'],
                    is_available=True
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [SUCCESS] {username} | Dr. {user.get_full_name()} | {profile['spec']} | {profile['dept']}"
                    )
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'[+] Successfully created {created_count} doctor accounts!'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Login Credentials:'))
        self.stdout.write(self.style.WARNING('  Username: doctor001, doctor002, doctor003, etc.'))
        self.stdout.write(self.style.WARNING('  Password: doctor@123'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
