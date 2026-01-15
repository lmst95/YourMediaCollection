#!/usr/bin/env python
"""
Script to create Django migrations without running a database.
This generates migration files based on model definitions.
"""

import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourmedia.settings.development')

# Setup Django
django.setup()

from django.core.management import call_command

print("=" * 60)
print("Creating Django Migrations")
print("=" * 60)
print()

# Create migrations for each app
apps = [
    'accounts',
    'media_catalog',
    'collections',
    'data_sync',
    'social',
    'recommendations',
]

for app in apps:
    print(f"Creating migrations for: {app}")
    try:
        call_command('makemigrations', app, verbosity=2)
        print(f"✓ Migrations created for {app}")
    except Exception as e:
        print(f"✗ Error creating migrations for {app}: {e}")
    print()

print("=" * 60)
print("Migration creation complete!")
print("=" * 60)
print()
print("Next steps:")
print("1. Review the generated migration files in each app's migrations/ folder")
print("2. Start Docker services: docker-compose up -d")
print("3. Run migrations: python manage.py migrate")
print()
