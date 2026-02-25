"""
Comprehensive test suite for Habit Tracker Platform
Tests all major functionality described in README.md
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from habits.models import Habit, HabitLog
import uuid


class ModelTests(TestCase):
    """Test Habit and HabitLog models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_habit_creation(self):
        """Test creating a habit with all fields"""
        habit = Habit.objects.create(
            user=self.user,
            name='Morning Workout',
            description='30 min exercise',
            frequency='daily'
        )
        self.assertEqual(habit.name, 'Morning Workout')
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.frequency, 'daily')
        self.assertIsInstance(habit.id, uuid.UUID)
        self.assertEqual(str(habit), 'Morning Workout')
    
    def test_habit_frequency_choices(self):
        """Test valid frequency choices"""
        daily_habit = Habit.objects.create(
            user=self.user,
            name='Daily Habit',
            frequency='daily'
        )
        weekly_habit = Habit.objects.create(
            user=self.user,
            name='Weekly Habit',
            frequency='weekly'
        )
        self.assertEqual(daily_habit.frequency, 'daily')
        self.assertEqual(weekly_habit.frequency, 'weekly')
    
    def test_habit_log_creation(self):
        """Test creating habit logs"""
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            frequency='daily'
        )
        today = date.today()
        log = HabitLog.objects.create(habit=habit, completed_at=today)
        self.assertEqual(log.habit, habit)
        self.assertEqual(log.completed_at, today)
        self.assertIsInstance(log.id, uuid.UUID)
    
    def test_habit_log_unique_constraint(self):
        """Test that duplicate logs for same day are prevented"""
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            frequency='daily'
        )
        today = date.today()
        
        # Create first log
        log1 = HabitLog.objects.create(habit=habit, completed_at=today)
        
        # Try to create duplicate - should raise error
        with self.assertRaises(Exception):
            HabitLog.objects.create(habit=habit, completed_at=today)
    
    def test_habit_deletion_cascades(self):
        """Test that deleting habit also deletes logs"""
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            frequency='daily'
        )
        today = date.today()
        HabitLog.objects.create(habit=habit, completed_at=today)
        
        habit_id = habit.id
        habit.delete()
        
        self.assertEqual(Habit.objects.filter(id=habit_id).count(), 0)
        self.assertEqual(HabitLog.objects.filter(habit_id=habit_id).count(), 0)


class AuthenticationTests(APITestCase):
    """Test JWT authentication flow"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='authuser',
            password='authpass123',
            email='auth@example.com'
        )
    
    def test_obtain_token_pair(self):
        """Test obtaining JWT tokens"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_obtain_token_invalid_credentials(self):
        """Test token endpoint with invalid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'authuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token(self):
        """Test refreshing access token"""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class HabitAPITests(APITestCase):
    """Test Habit CRUD API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test habits
        self.habit1 = Habit.objects.create(
            user=self.user,
            name='Exercise',
            description='Daily workout',
            frequency='daily'
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            name='Reading',
            frequency='daily'
        )
        # Other user's habit (should not be accessible)
        self.other_habit = Habit.objects.create(
            user=self.other_user,
            name='Other Habit',
            frequency='daily'
        )
    
    def test_list_habits(self):
        """Test GET /api/v1/habits/ - List user's habits"""
        url = reverse('habit-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only user's habits
    
    def test_list_habits_unauthenticated(self):
        """Test that unauthenticated users cannot access habits"""
        self.client.credentials()  # Remove authentication
        url = reverse('habit-list')
        response = self.client.get(url)
        
        # DRF returns 403 Forbidden when using SessionAuthentication without JWT
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_habit(self):
        """Test POST /api/v1/habits/ - Create new habit"""
        url = reverse('habit-list')
        data = {
            'name': 'Meditation',
            'description': 'Daily meditation practice',
            'frequency': 'daily'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 3)
        self.assertEqual(response.data['name'], 'Meditation')
    
    def test_retrieve_habit(self):
        """Test GET /api/v1/habits/{id}/ - Retrieve specific habit"""
        url = reverse('habit-detail', args=[self.habit1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Exercise')
        self.assertIn('completed_today', response.data)
    
    def test_retrieve_other_users_habit(self):
        """Test that users cannot access other users' habits"""
        url = reverse('habit-detail', args=[self.other_habit.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_habit(self):
        """Test PUT /api/v1/habits/{id}/ - Update habit"""
        url = reverse('habit-detail', args=[self.habit1.id])
        data = {
            'name': 'Updated Exercise',
            'description': 'New description',
            'frequency': 'weekly'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.name, 'Updated Exercise')
        self.assertEqual(self.habit1.frequency, 'weekly')
    
    def test_partial_update_habit(self):
        """Test PATCH /api/v1/habits/{id}/ - Partial update"""
        url = reverse('habit-detail', args=[self.habit1.id])
        data = {'name': 'Partially Updated'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.name, 'Partially Updated')
        self.assertEqual(self.habit1.frequency, 'daily')  # Unchanged
    
    def test_delete_habit(self):
        """Test DELETE /api/v1/habits/{id}/ - Delete habit"""
        url = reverse('habit-detail', args=[self.habit1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=self.habit1.id).count(), 0)


class HabitLogAPITests(APITestCase):
    """Test habit logging functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='loguser',
            password='logpass123'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            frequency='daily'
        )
    
    def test_log_habit_completion(self):
        """Test POST /api/v1/habits/{id}/log/ - Log completion"""
        url = reverse('habit-log', args=[self.habit.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'habit logged')
        
        # Check log was created
        today = date.today()
        self.assertTrue(
            HabitLog.objects.filter(habit=self.habit, completed_at=today).exists()
        )
    
    def test_log_habit_idempotent(self):
        """Test that logging same habit twice doesn't create duplicates"""
        url = reverse('habit-log', args=[self.habit.id])
        
        # Log twice
        response1 = self.client.post(url)
        response2 = self.client.post(url)
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Should still only have one log
        today = date.today()
        self.assertEqual(
            HabitLog.objects.filter(habit=self.habit, completed_at=today).count(),
            1
        )


class AnalyticsAPITests(APITestCase):
    """Test analytics API endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='analyticsuser',
            password='analyticspass123'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create habits
        self.habit1 = Habit.objects.create(
            user=self.user,
            name='Habit 1',
            frequency='daily'
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            name='Habit 2',
            frequency='daily'
        )
        
        # Create logs
        today = date.today()
        HabitLog.objects.create(habit=self.habit1, completed_at=today)
        HabitLog.objects.create(habit=self.habit1, completed_at=today - timedelta(days=2))
        HabitLog.objects.create(habit=self.habit2, completed_at=today - timedelta(days=1))
        HabitLog.objects.create(habit=self.habit1, completed_at=today - timedelta(days=10))
    
    def test_analytics_endpoint(self):
        """Test GET /api/v1/analytics/ - Get user analytics"""
        url = reverse('habit-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_habits', response.data)
        self.assertIn('total_completions', response.data)
        self.assertIn('last_7_days_completions', response.data)
        self.assertIn('per_habit', response.data)
        
        self.assertEqual(response.data['total_habits'], 2)
        self.assertEqual(response.data['total_completions'], 4)
        self.assertEqual(response.data['last_7_days_completions'], 3)  # Last 7 days
    
    def test_analytics_unauthenticated(self):
        """Test that analytics requires authentication"""
        self.client.credentials()
        url = reverse('habit-analytics')
        response = self.client.get(url)
        
        # DRF may return either 401 or 403 depending on authentication backend
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class DashboardViewTests(TestCase):
    """Test HTML dashboard views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dashuser',
            password='dashpass123'
        )
        self.client = Client()
        
        self.habit1 = Habit.objects.create(
            user=self.user,
            name='Habit 1',
            frequency='daily'
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            name='Habit 2',
            frequency='daily'
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires login"""
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view(self):
        """Test GET /api/v1/dashboard/ - User dashboard"""
        self.client.login(username='dashuser', password='dashpass123')
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Habit 1')
        self.assertContains(response, 'Habit 2')
    
    def test_mark_complete(self):
        """Test POST /api/v1/dashboard/complete/{id}/ - Toggle completion"""
        self.client.login(username='dashuser', password='dashpass123')
        url = reverse('mark-complete', args=[self.habit1.id])
        
        # Mark complete
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirects back
        
        # Check log created
        today = date.today()
        self.assertTrue(
            HabitLog.objects.filter(habit=self.habit1, completed_at=today).exists()
        )
        
        # Mark uncomplete
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        # Check log deleted
        self.assertFalse(
            HabitLog.objects.filter(habit=self.habit1, completed_at=today).exists()
        )


class AdminDashboardTests(TestCase):
    """Test admin analytics dashboard"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass123'
        )
        self.client = Client()
        
        # Create test data
        habit = Habit.objects.create(
            user=self.regular_user,
            name='Test Habit',
            frequency='daily'
        )
        today = date.today()
        HabitLog.objects.create(habit=habit, completed_at=today)
    
    def test_admin_dashboard_requires_staff(self):
        """Test that admin dashboard requires staff permissions"""
        self.client.login(username='regular', password='regularpass123')
        url = reverse('admin-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_admin_dashboard_view(self):
        """Test admin dashboard displays analytics"""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('admin-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Total Users')
        self.assertContains(response, 'Total Habits')
        self.assertContains(response, 'Total Completions')


class SerializerTests(TestCase):
    """Test serializers"""
    
    def setUp(self):
        from habits.serializers import HabitSerializer
        
        self.user = User.objects.create_user(
            username='serializeruser',
            password='pass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            frequency='daily'
        )
    
    def test_habit_serializer_completed_today(self):
        """Test that completed_today field works correctly"""
        from habits.serializers import HabitSerializer
        
        # Not completed yet
        serializer = HabitSerializer(self.habit)
        self.assertFalse(serializer.data['completed_today'])
        
        # Mark as completed
        today = date.today()
        HabitLog.objects.create(habit=self.habit, completed_at=today)
        
        serializer = HabitSerializer(self.habit)
        self.assertTrue(serializer.data['completed_today'])


class IntegrationTests(APITestCase):
    """End-to-end integration tests"""
    
    def test_complete_user_flow(self):
        """Test complete workflow: register -> create habit -> log -> view analytics"""
        # Create user
        user = User.objects.create_user(
            username='flowuser',
            password='flowpass123'
        )
        
        # Get token
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create habit
        create_url = reverse('habit-list')
        habit_data = {
            'name': 'Morning Run',
            'description': '5km run',
            'frequency': 'daily'
        }
        response = self.client.post(create_url, habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit_id = response.data['id']
        
        # Log habit
        log_url = reverse('habit-log', args=[habit_id])
        response = self.client.post(log_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check analytics
        analytics_url = reverse('habit-analytics')
        response = self.client.get(analytics_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_habits'], 1)
        self.assertEqual(response.data['total_completions'], 1)
        self.assertEqual(response.data['last_7_days_completions'], 1)
