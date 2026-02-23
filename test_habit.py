import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habits.models import Habit

# Create a test user if doesn't exist
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f'Created new user: {user.username}')
else:
    print(f'User already exists: {user.username}')

# Create a test habit
habit = Habit.objects.create(
    user=user,
    name='Daily Exercise',
    description='30 minutes of physical activity',
    frequency='daily'
)
print(f'\n✅ Successfully created habit: {habit.name}')
print(f'   ID: {habit.id}')
print(f'   Description: {habit.description}')
print(f'   Frequency: {habit.frequency}')
print(f'   User: {habit.user.username}')

# Show all habits
print(f'\nTotal habits in database: {Habit.objects.count()}')
for h in Habit.objects.all():
    print(f'  - {h.name} ({h.frequency}) - User: {h.user.username}')
