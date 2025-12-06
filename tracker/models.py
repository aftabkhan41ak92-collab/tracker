
from django.db import models
from django.contrib.auth.models import User

class HealthRecord(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')  # 👈 add this line
    weight = models.FloatField()
    height_cm = models.FloatField()
    bmi = models.FloatField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%Y-%m-%d')}"
