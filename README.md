# 🚀 Habit Tracker Platform  
### Production-Style Django Backend + Web Dashboard

A secure, production-oriented habit tracking platform built with **Django** and **Django REST Framework**.


# 🏗 Architecture Overview

- RESTful API design
- JWT-based authentication (stateless)
- User-scoped data access
- Relational database modeling
- Versioned API routing (`/api/v1/`)
- Server-rendered dashboards (Django templates)
- Aggregation-based analytics
- Admin-level analytics dashboard

---

# 🛠 Tech Stack

- Python 3.10
- Django 5.x
- Django REST Framework
- SimpleJWT (token authentication)
- SQLite (development)
- Django Template Engine (HTML dashboards)

---

# 🔐 Authentication & Security

Implements stateless JWT authentication:

- `POST /api/token/` → Obtain access + refresh tokens  
- `POST /api/token/refresh/` → Refresh access token  

All protected endpoints require:
Authorization: Bearer <access_token>


Security architecture includes:

- Per-user queryset filtering
- Authenticated-only API access
- Login-protected HTML dashboards
- Database-level integrity constraints

---

# 📡 API Endpoints

Base route:
/api/v1/


---

## 🗂 Habit Management

- `GET /habits/` → List authenticated user’s habits  
- `POST /habits/` → Create habit  
- `GET /habits/{id}/` → Retrieve habit  
- `PUT/PATCH /habits/{id}/` → Update habit  
- `DELETE /habits/{id}/` → Delete habit  

---

## ✅ Habit Logging

- `POST /habits/{id}/log/` → Toggle habit completion for today  

Uses a database constraint to prevent duplicate logs per day.

---

## 📊 Analytics API

- `GET /analytics/`

Returns:

- Total habits
- Total completions
- Last 7-day completion count
- Per-habit completion breakdown

Demonstrates use of:

- `annotate()`
- `Count()`
- Date filtering
- Aggregation queries

---

# 🖥 Web Dashboards

## 👤 User Dashboard  
Route:
/api/v1/dashboard/


Features:

- Displays all user habits
- Toggle complete / uncomplete
- Daily completion tracking
- Completion percentage progress bar
- Clean modern UI
- Login required

Demonstrates:

- Server-rendered HTML with Django templates
- Conditional rendering
- Form-based POST actions
- Real-time percentage calculation
- User-scoped filtering

---

## 🛠 Admin Analytics Dashboard  
Route:
/api/v1/admin-dashboard/


Features:

- Total users
- Total habits
- Total completions
- Most completed habits
- Clean card-based analytics layout
- Admin-only access

Demonstrates:

- Cross-user aggregation
- Advanced ORM queries
- `annotate()` and `Count()` usage
- Permission-based view protection

---

# 🗄 Database Design

## Habit

- UUID primary key
- Foreign key → User
- Name
- Description
- Frequency (daily / weekly)
- Created timestamp

---

## HabitLog

- UUID primary key
- Foreign key → Habit
- Completion date
- Unique constraint on (`habit`, `completed_at`)
- Related name: `logs`

Prevents duplicate daily completions at the database level.

---

# 🧠 Engineering Concepts Demonstrated

This project demonstrates:

- Full backend system ownership
- Secure token-based authentication
- Per-user data isolation
- Clean MVC separation
- RESTful resource modeling
- Aggregation & analytics queries
- Server-side dashboard rendering
- Database-level data integrity
- API versioning
- Production-style architecture structure

---

# 🚀 Local Development

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Admin Panel:
http://127.0.0.1:8000/admin/
User Dashboard:
http://127.0.0.1:8000/api/v1/dashboard/
Admin Analytics Dashboard:
http://127.0.0.1:8000/api/v1/admin-dashboard/
🧩 Future Improvements
Streak tracking

Graph-based analytics

Email reminders

Pagination

PostgreSQL production deployment

Docker containerization