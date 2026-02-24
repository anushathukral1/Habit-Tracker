from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    HabitViewSet,
    HabitAnalyticsView,
    dashboard_view,
    mark_complete,
)

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("analytics/", HabitAnalyticsView.as_view(), name="habit-analytics"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/complete/<uuid:habit_id>/", mark_complete, name="mark-complete"),
]

urlpatterns += router.urls