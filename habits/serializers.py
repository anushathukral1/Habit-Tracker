from rest_framework import serializers
from .models import Habit, HabitLog


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at")


