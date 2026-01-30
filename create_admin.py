#!/usr/bin/env python
"""Create admin superuser"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@hospital.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='ADMIN'
    )
    print(f'✅ Superuser created: {user.username}')
else:
    print('⚠️  Admin user already exists')
