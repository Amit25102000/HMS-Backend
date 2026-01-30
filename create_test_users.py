"""
Script to create test users for all roles
Run with: python manage.py shell < create_test_users.py
"""
from apps.authentication.models import User

# Create test users with all roles
users_to_create = [
    {'username': 'admin', 'password': 'admin123', 'role': 'ADMIN', 'first_name': 'Admin', 'last_name': 'User', 'email': 'admin@hospital.com'},
    {'username': 'doctor', 'password': 'doctor123', 'role': 'DOCTOR', 'first_name': 'John', 'last_name': '  Doe', 'email': 'doctor@hospital.com'},
    {'username': 'staff', 'password': 'staff123', 'role': 'STAFF', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'staff@hospital.com'},
    {'username': 'receptionist', 'password': 'receptionist123', 'role': 'RECEPTIONIST', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'receptionist@hospital.com'},
]

for user_data in users_to_create:
    username = user_data['username']
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists, skipping...")
        continue
    
    # Create user
    user = User.objects.create_user(
        username=user_data['username'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        role=user_data['role']
    )
    print(f"Created user: {username} ({user_data['role']})")

print("\nTest users created successfully!")
print("\nLogin credentials:")
print("Admin: admin / admin123")
print("Doctor: doctor / doctor123")
print("Staff: staff / staff123")
print("Receptionist: receptionist / receptionist123")
