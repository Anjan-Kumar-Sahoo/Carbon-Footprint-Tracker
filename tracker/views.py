from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CommuteRecordForm
from .models import CommuteRecord
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import os

# Load the pre-trained model
model_path = os.path.join(os.path.dirname(__file__), 'ml_model', 'model.pkl')
# Check if the model file exists before loading
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None # Handle case where model is not yet trained

@login_required
def dashboard(request):
    commute_records = CommuteRecord.objects.filter(user=request.user).order_by("-date")
    return render(request, "tracker/dashboard.html", {"commute_records": commute_records})

@login_required
def add_record(request):
    if request.method == "POST":
        form = CommuteRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            # Predict emission using the loaded model
            if model:
                # Example: record.predicted_emission = model.predict([[record.distance, record.fuel_efficiency]])
                record.predicted_emission = record.distance * record.fuel_efficiency * 0.2 # Dummy calculation
            else:
                record.predicted_emission = 0.0 # Default if model not loaded
            record.save()
            return redirect("result", record_id=record.id)
    else:
        form = CommuteRecordForm()
    return render(request, "tracker/add_record.html", {"form": form})

@login_required
def result(request, record_id):
    record = get_object_or_404(CommuteRecord, id=record_id, user=request.user)

    # Generate dummy chart (replace with actual data visualization)
    # For example, compare user's emission with average emission
    avg_emission = CommuteRecord.objects.filter(user=request.user).exclude(id=record_id).aggregate(models.Avg("predicted_emission"))["predicted_emission__avg"]
    if avg_emission is None:
        avg_emission = 0

    labels = ["Your Emission", "Average Emission"]
    values = [record.predicted_emission, avg_emission]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=["blue", "green"])
    plt.ylabel("CO2 Emission (kg)")
    plt.title("Your Emission vs. Average Emission")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, f"chart_{record.id}.png")
    plt.savefig(chart_path)
    plt.close()

    return render(request, "tracker/result.html", {"record": record, "chart_path": f"/media/charts/chart_{record.id}.png"})


