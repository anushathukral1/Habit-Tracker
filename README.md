# 🚀 Habit Tracker API (Production-Style Backend)

A secure, production-oriented REST API for tracking user habits, built with Django and Django REST Framework.

This project demonstrates full ownership of backend API development including authentication, database modeling, user isolation, and scalable architecture.

---

## 🏗 Architecture Overview

- RESTful API design
- JWT-based authentication
- User-scoped data access
- Relational database modeling
- Modular Django app structure
- Versioned API routing (`/api/v1/`)

---

## 🛠 Tech Stack

- Python 3.10  
- Django  
- Django REST Framework  
- SimpleJWT (token authentication)  
- SQLite (development)  

---

## 🔐 Authentication & Security

Implements stateless JWT authentication:

- `POST /api/token/` → Obtain access + refresh tokens  
- `POST /api/token/refresh/` → Refresh access token  

All habit endpoints require:
Authorization: Bearer <access_token>


User data is fully isolated at the queryset level.

---

## 📡 API Endpoints

Base route:
/api/v1/


### Habit Management

- `GET /habits/` → List authenticated user’s habits  
- `POST /habits/` → Create habit  
- `GET /habits/{id}/` → Retrieve habit  
- `PUT/PATCH /habits/{id}/` → Update habit  
- `DELETE /habits/{id}/` → Delete habit  

### Habit Logging

- `POST /habits/{id}/log/` → Record habit completion  

---

## 🗄 Database Design

### Habit

- UUID primary key  
- Foreign key → User  
- Name  
- Description  
- Frequency (daily / weekly)  
- Created timestamp  

### HabitLog

- UUID primary key  
- Foreign key → Habit  
- Completion date  
- Unique constraint on (habit, completed_at)  

---

## 🧠 Key Engineering Concepts Demonstrated

- End-to-end backend ownership  
- Secure token-based authentication  
- Per-user data filtering  
- Clean separation of concerns (models, serializers, views)  
- RESTful resource design  
- Database integrity constraints  
- API versioning for forward compatibility  

---

## 🚀 Local Development

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Admin UI:
http://127.0.0.1:8000/admin/
