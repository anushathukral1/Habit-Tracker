import uuid
from django.db import models
from django.contrib.auth.models import User


class Habit(models.Model):
    FREQUENCY_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HabitLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    completed_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("habit", "completed_at")