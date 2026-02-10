from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Create superuser if doesn't exist
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@hospital.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='ADMIN'
    )
    # Add to Admin group
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    admin.groups.add(admin_group)
    print(f'✓ Created admin user: {admin.username}')
else:
    print('Admin user already exists')

# Create test doctor
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
    print(f'✓ Created doctor user: {doctor.username}')
else:
    print('Doctor user already exists')

# List all users
print('\n--- All Users ---')
for user in User.objects.all():
    print(f'{user.username} - {user.get_role_display()} - Active: {user.is_active}')
