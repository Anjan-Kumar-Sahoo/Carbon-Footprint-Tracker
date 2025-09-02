
from django.db import models
from django.contrib.auth.models import User

class Badge(models.Model):
    ECO_WARRIOR = 'eco_warrior'
    BADGE_CHOICES = [
        (ECO_WARRIOR, 'Eco Warrior 🌱'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge_type = models.CharField(max_length=50, choices=BADGE_CHOICES)
    date_awarded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"

class MonthlySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    total_emission = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: {self.total_emission:.2f} kg CO₂"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_co2_goal = models.FloatField(default=100.0, help_text="Monthly CO₂ emission goal in kg")
    preferred_transport = models.CharField(max_length=50, blank=True, help_text="Preferred eco-friendly transport")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class CommuteRecord(models.Model):
    TRANSPORT_CHOICES = [
        ('car_petrol', 'Car (Petrol)'),
        ('car_diesel', 'Car (Diesel)'),
        ('car_hybrid', 'Car (Hybrid)'),
        ('car_electric', 'Car (Electric)'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('bicycle', 'Bicycle'),
        ('walking', 'Walking'),
        ('taxi', 'Taxi'),
        ('auto_rickshaw', 'Auto Rickshaw'),
        ('metro', 'Metro/Subway'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode_of_transport = models.CharField(max_length=50, choices=TRANSPORT_CHOICES)
    distance = models.FloatField(help_text="Distance traveled in kilometers")
    fuel_efficiency = models.FloatField(help_text="Mileage in km/L (kilometers per liter)")
    date = models.DateField(auto_now_add=True)
    predicted_emission = models.FloatField(help_text="Predicted CO2 emission in kg")
    weather = models.CharField(max_length=20, choices=[('clear', 'Clear'), ('rainy', 'Rainy'), ('snowy', 'Snowy')], default='clear')
    traffic_intensity = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    road_type = models.CharField(max_length=20, choices=[('city', 'City'), ('highway', 'Highway')], default='city')

    def __str__(self):
        return f"{self.user.username} - {self.get_mode_of_transport_display()}"

    def get_eco_alternatives(self):
        """Calculate CO₂ savings for eco-friendly alternatives"""
        alternatives = {
            'bus': {'emission_factor': 0.08, 'name': 'Bus'},  # kg CO₂ per km
            'train': {'emission_factor': 0.04, 'name': 'Train'},
            'metro': {'emission_factor': 0.03, 'name': 'Metro'},
            'bicycle': {'emission_factor': 0.0, 'name': 'Bicycle'},
            'walking': {'emission_factor': 0.0, 'name': 'Walking'},
        }
        
        suggestions = []
        current_emission = self.predicted_emission
        
        for alt_key, alt_data in alternatives.items():
            if alt_key != self.mode_of_transport:  # Don't suggest the same transport
                alt_emission = self.distance * alt_data['emission_factor']
                saving = current_emission - alt_emission
                if saving > 0.1:  # Only suggest if saving is significant
                    suggestions.append({
                        'transport': alt_data['name'],
                        'emission': alt_emission,
                        'saving': saving,
                        'percentage': (saving / current_emission) * 100 if current_emission > 0 else 0
                    })
        
        return sorted(suggestions, key=lambda x: x['saving'], reverse=True)
