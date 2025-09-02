from django import forms
from .models import CommuteRecord, UserProfile

class CommuteRecordForm(forms.ModelForm):
    class Meta:
        model = CommuteRecord
        fields = (
            "mode_of_transport",
            "distance",
            "fuel_efficiency",
            "weather",
            "traffic_intensity",
            "road_type",
        )
        labels = {
            'mode_of_transport': 'Mode of Transport',
            'distance': 'Distance (km)',
            'fuel_efficiency': 'Mileage (km/L)',
            'weather': 'Weather',
            'traffic_intensity': 'Traffic Intensity',
            'road_type': 'Road Type',
        }
        widgets = {
            'mode_of_transport': forms.Select(attrs={'class': 'form-control'}),
            'distance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'fuel_efficiency': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'placeholder': 'e.g., 15.5'}),
            'weather': forms.Select(attrs={'class': 'form-control'}),
            'traffic_intensity': forms.Select(attrs={'class': 'form-control'}),
            'road_type': forms.Select(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('monthly_co2_goal', 'preferred_transport')
        labels = {
            'monthly_co2_goal': 'Monthly CO₂ Goal (kg)',
            'preferred_transport': 'Preferred Eco Transport'
        }
        widgets = {
            'monthly_co2_goal': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'min': '10', 
                'max': '1000',
                'placeholder': 'e.g., 100'
            }),
            'preferred_transport': forms.Select(
                choices=[
                    ('', 'Select preferred transport'),
                    ('bus', 'Bus'),
                    ('train', 'Train'),
                    ('metro', 'Metro'),
                    ('bicycle', 'Bicycle'),
                    ('walking', 'Walking'),
                ],
                attrs={'class': 'form-control'}
            )
        }


