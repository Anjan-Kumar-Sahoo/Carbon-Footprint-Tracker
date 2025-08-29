from django import forms
from .models import CommuteRecord

class CommuteRecordForm(forms.ModelForm):
    class Meta:
        model = CommuteRecord
        fields = ("mode_of_transport", "distance", "fuel_efficiency")


