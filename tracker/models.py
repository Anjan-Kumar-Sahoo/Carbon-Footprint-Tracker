from django.db import models
from django.contrib.auth.models import User

class CommuteRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode_of_transport = models.CharField(max_length=50)
    distance = models.FloatField()
    fuel_efficiency = models.FloatField()
    date = models.DateField(auto_now_add=True)
    predicted_emission = models.FloatField()

    def __str__(self):
        return f"{self.user.username}"
