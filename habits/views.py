from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import HabitLog, Habit
from .serializers import HabitSerializer

from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required



@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()
    total_habits = Habit.objects.count()
    total_logs = HabitLog.objects.count()

    top_users = (
        User.objects
        .annotate(total_logs=Count("habits__logs"))
        .order_by("-total_logs")[:5]
    )

    top_habits = (
        Habit.objects
        .annotate(total_logs=Count("logs"))
        .order_by("-total_logs")[:5]
    )

    return render(request, "habits/admin_dashboard.html", {
        "total_users": total_users,
        "total_habits": total_habits,
        "total_logs": total_logs,
        "top_users": top_users,
        "top_habits": top_habits,
    })



class HabitAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_habits = Habit.objects.filter(user=user).count()
        total_logs = HabitLog.objects.filter(habit__user=user).count()

        last_week = now().date() - timedelta(days=7)
        weekly_logs = HabitLog.objects.filter(
            habit__user=user,
            completed_at__gte=last_week
        ).count()

        habit_breakdown = (
            HabitLog.objects
            .filter(habit__user=user)
            .values("habit__name")
            .annotate(count=Count("id"))
        )

        return Response({
            "total_habits": total_habits,
            "total_completions": total_logs,
            "last_7_days_completions": weekly_logs,
            "per_habit": habit_breakdown
        })



class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def log(self, request, pk=None):
        habit = self.get_object()

        HabitLog.objects.get_or_create(
            habit=habit,
            completed_at=now().date()
        )

        return Response({"status": "habit logged"})



from datetime import timedelta

@login_required
def dashboard_view(request):
    habits = Habit.objects.filter(user=request.user)
    today = now().date()

    habit_data = []
    completed_count = 0

    for habit in habits:
        # Completed today?
        completed_today = HabitLog.objects.filter(
            habit=habit,
            completed_at=today
        ).exists()

        if completed_today:
            completed_count += 1

        streak = 0
        day = today

        while HabitLog.objects.filter(
            habit=habit,
            completed_at=day
        ).exists():
            streak += 1
            day -= timedelta(days=1)

        habit_data.append({
            "id": habit.id,
            "name": habit.name,
            "completed_today": completed_today,
            "streak": streak
        })

    total = habits.count()

    percentage = 0
    if total > 0:
        percentage = int((completed_count / total) * 100)

    return render(request, "habits/dashboard.html", {
        "habits": habit_data,
        "completed": completed_count,
        "total": total,
        "percentage": percentage
    })


@login_required
def mark_complete(request, habit_id):
    habit = Habit.objects.get(id=habit_id, user=request.user)
    today = now().date()

    log = HabitLog.objects.filter(
        habit=habit,
        completed_at=today
    ).first()

    if log:
        log.delete()
    else:
        HabitLog.objects.create(
            habit=habit,
            completed_at=today
        )

    return redirect("dashboard")