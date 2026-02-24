from rest_framework import serializers
from .models import Habit, HabitLog
from django.utils.timezone import now


class HabitSerializer(serializers.ModelSerializer):
    completed_today = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["user"]

    def get_completed_today(self, obj):
        today = now().date()
        return HabitLog.objects.filter(
            habit=obj,
            completed_at=today
        ).exists()


class HabitLogSerializer(serializers.ModelSerializer):
    habit_name = serializers.CharField(source="habit.name", read_only=True)

    class Meta:
        model = HabitLog
        fields = ["id", "habit", "habit_name", "completed_at"]