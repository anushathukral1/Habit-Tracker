# Database Access Guide for Your Habit Tracker

## 🗄️ Database Information

**Database Type:** SQLite3 (Django's default database)  
**Database Location:** `/Users/anushathukral/django_root_folder/db.sqlite3`

---

## ✅ Test Results

**Project tested successfully!** I added a test habit to your database.

### Current Database Contents (4 habits total):
1. **Gym** - "Workout 30 mins a day" (daily) - User: anushathukral
2. **Wework** - "Work 9-9-6" (daily) - User: anushathukral  
3. **Daily Exercise** - "30 minutes of physical activity" (daily) - User: testuser
4. **Daily Exercise** (duplicate) - User: testuser

---

## 🔍 How to Access Your Database

### Method 1: Django Shell (Recommended for Django projects)
```bash
python manage.py shell
```

Then in the shell:
```python
from habits.models import Habit, HabitLog
from django.contrib.auth.models import User

# View all habits
habits = Habit.objects.all()
for habit in habits:
    print(f"{habit.name} - {habit.frequency} - User: {habit.user.username}")

# View habits for a specific user
user_habits = Habit.objects.filter(user__username='anushathukral')

# Create a new habit
user = User.objects.get(username='anushathukral')
new_habit = Habit.objects.create(
    user=user,
    name='Read Books',
    description='Read for 30 minutes',
    frequency='daily'
)
```

### Method 2: SQLite Command Line
```bash
sqlite3 db.sqlite3
```

Useful SQLite commands:
```sql
-- List all tables
.tables

-- View all habits with user info
SELECT h.name, h.description, h.frequency, u.username 
FROM habits_habit h 
JOIN auth_user u ON h.user_id = u.id;

-- Count total habits
SELECT COUNT(*) FROM habits_habit;

-- View habit logs
SELECT * FROM habits_habitlog;

-- Exit SQLite
.quit
```

### Method 3: Django Admin Interface
1. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Visit: http://127.0.0.1:8000/admin/

4. Register your models in `habits/admin.py`:
   ```python
   from django.contrib import admin
   from .models import Habit, HabitLog

   @admin.register(Habit)
   class HabitAdmin(admin.ModelAdmin):
       list_display = ['name', 'user', 'frequency', 'created_at']
       list_filter = ['frequency', 'created_at']
       search_fields = ['name', 'description']

   @admin.register(HabitLog)
   class HabitLogAdmin(admin.ModelAdmin):
       list_display = ['habit', 'completed_at']
       list_filter = ['completed_at']
   ```

### Method 4: VS Code SQLite Extension
1. Install "SQLite" extension in VS Code
2. Right-click on `db.sqlite3` file
3. Select "Open Database"
4. Explore tables visually

---

## 🚀 Running Your Project

### Start the development server:
```bash
python manage.py runserver
```

### API Endpoints (based on your code):
- `GET /habits/` - List all habits for authenticated user
- `POST /habits/` - Create a new habit
- `GET /habits/{id}/` - Get specific habit
- `PUT/PATCH /habits/{id}/` - Update habit
- `DELETE /habits/{id}/` - Delete habit
- `POST /habits/{id}/log/` - Log a habit completion

---

## 📊 Database Schema

### Habit Model
- `id` - UUID (Primary Key)
- `user` - Foreign Key to User
- `name` - CharField (max 255)
- `description` - TextField
- `frequency` - CharField (choices: daily, weekly)
- `created_at` - DateTimeField

### HabitLog Model
- `id` - UUID (Primary Key)
- `habit` - Foreign Key to Habit
- `completed_at` - DateField
- Unique constraint on (habit, completed_at)

---

## 🔧 Useful Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Check for issues
python manage.py check
```

---

## 💡 Tips

1. **Backup your database**: Copy `db.sqlite3` file regularly
2. **For production**: Consider PostgreSQL or MySQL instead of SQLite
3. **Test users created**: 
   - Username: `testuser`, Password: `testpass123`
   - Your existing user: `anushathukral`
