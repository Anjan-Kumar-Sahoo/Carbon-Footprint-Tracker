from django.http import HttpResponse
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .forms import CommuteRecordForm, UserProfileForm
from .models import CommuteRecord, UserProfile
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import CommuteRecordSerializer

# Load the pre-trained model
model_path = os.path.join(os.path.dirname(__file__), 'ml_model', 'model.pkl')
# Check if the model file exists before loading
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None # Handle case where model is not yet trained

def home(request):
    """Home page view"""
    return render(request, "tracker/home.html")

@login_required
def profile_settings(request):
    """User profile settings for goals and preferences"""
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'monthly_co2_goal': 100.0}
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)

    # Calculate lifetime emissions saved
    records = CommuteRecord.objects.filter(user=request.user)
    lifetime_saved = 0.0
    for record in records:
        alternatives = record.get_eco_alternatives()
        if alternatives:
            best = alternatives[0]
            lifetime_saved += best['saving']

    # Calculate lifetime emissions
    lifetime_emission = sum(r.predicted_emission for r in records)

    return render(request, 'tracker/profile_settings.html', {
        'form': form,
        'profile': profile,
        'lifetime_saved': lifetime_saved,
        'lifetime_emission': lifetime_emission,
    })

@login_required
def export_data(request):
    format = request.GET.get('format', 'csv')
    from .models import MonthlySummary
    summaries = MonthlySummary.objects.filter(user=request.user).order_by('year', 'month')

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="emissions_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Month', 'Year', 'Total Emission (kg CO2)'])
        for s in summaries:
            writer.writerow([s.month, s.year, f"{s.total_emission:.2f}"])
        return response
    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="emissions_summary.pdf"'
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, "Monthly Emissions Summary")
        p.setFont("Helvetica", 12)
        y = 720
        p.drawString(50, y, "Month")
        p.drawString(150, y, "Year")
        p.drawString(250, y, "Total Emission (kg CO2)")
        y -= 20
        for s in summaries:
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = 750
            p.drawString(50, y, str(s.month))
            p.drawString(150, y, str(s.year))
            p.drawString(250, y, f"{s.total_emission:.2f}")
            y -= 20
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    else:
        return HttpResponse("Invalid format", status=400)

@login_required
def dashboard(request):
    import calendar
    from datetime import date
    from .models import MonthlySummary, CommuteRecord, UserProfile
    from django.contrib.auth.models import User
    import os
    import matplotlib.pyplot as plt

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'monthly_co2_goal': 100.0}
    )

    # Calculate monthly data
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    monthly_records = CommuteRecord.objects.filter(user=request.user, date__range=[month_start, month_end])
    total_monthly_emission = sum(r.predicted_emission for r in monthly_records)
    monthly_goal = profile.monthly_co2_goal
    progress = min(int((total_monthly_emission / monthly_goal) * 100), 100) if monthly_goal else 0

    # Emission by transport type for chart
    transport_emissions = {}
    for r in monthly_records:
        t = r.get_mode_of_transport_display()
        transport_emissions[t] = transport_emissions.get(t, 0) + r.predicted_emission

    # Generate bar chart if there's data
    chart_path = ""
    if transport_emissions:
        chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'charts')
        os.makedirs(chart_dir, exist_ok=True)
        chart_file = os.path.join(chart_dir, f"monthly_transport_chart_{request.user.id}.png")
        plt.figure(figsize=(10, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        bars = plt.bar(transport_emissions.keys(), transport_emissions.values(), color=colors[:len(transport_emissions)])
        plt.ylabel("CO₂ Emission (kg)", fontsize=12)
        plt.title(f"Monthly Emissions by Transport Type ({today.strftime('%B %Y')})", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}kg', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        chart_path = f"/media/charts/monthly_transport_chart_{request.user.id}.png"

    # Monthly Emissions Trend Chart
    summaries = MonthlySummary.objects.filter(user=request.user).order_by('year', 'month')
    trend_labels = [f"{s.month}/{s.year}" for s in summaries]
    trend_values = [s.total_emission for s in summaries]
    trend_chart_path = ""
    if trend_labels and trend_values:
        trend_chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'charts')
        os.makedirs(trend_chart_dir, exist_ok=True)
        trend_chart_file = os.path.join(trend_chart_dir, f"emissions_trend_{request.user.id}.png")
        plt.figure(figsize=(10, 5))
        plt.bar(trend_labels, trend_values, color="#4ECDC4")
        plt.ylabel("CO₂ Emission (kg)", fontsize=12)
        plt.title("Monthly Emissions Trend", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        for i, v in enumerate(trend_values):
            plt.text(i, v + 0.5, f"{v:.1f}", ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(trend_chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        trend_chart_path = f"/media/charts/emissions_trend_{request.user.id}.png"

    # Enhanced suggestions for recent records
    recent_records = CommuteRecord.objects.filter(user=request.user).order_by("-date")[:10]
    enhanced_suggestions = {}
    for record in recent_records:
        alternatives = record.get_eco_alternatives()
        if alternatives:
            best_alternative = alternatives[0]
            enhanced_suggestions[record.id] = {
                'best': best_alternative,
                'all_alternatives': alternatives[:3]
            }

    commute_records = CommuteRecord.objects.filter(user=request.user).order_by("-date")
    total_records = commute_records.count()
    avg_daily_emission = total_monthly_emission / today.day if today.day > 0 else 0

    # Leaderboard: compare lifetime emissions saved across users
    users = User.objects.all()
    leaderboard = []
    for u in users:
        records = CommuteRecord.objects.filter(user=u)
        lifetime_saved = 0.0
        for record in records:
            alternatives = record.get_eco_alternatives()
            if alternatives:
                best = alternatives[0]
                lifetime_saved += best['saving']
        leaderboard.append({
            'username': u.username,
            'lifetime_saved': lifetime_saved
        })
    leaderboard = sorted(leaderboard, key=lambda x: x['lifetime_saved'], reverse=True)[:10]

    return render(request, "tracker/dashboard.html", {
        "commute_records": commute_records,
        "monthly_emission": total_monthly_emission,
        "monthly_goal": monthly_goal,
        "progress": progress,
        "transport_chart_path": chart_path,
        "trend_chart_path": trend_chart_path,
        "enhanced_suggestions": enhanced_suggestions,
        "total_records": total_records,
        "avg_daily_emission": avg_daily_emission,
        "current_month": today.strftime('%B %Y'),
        "profile": profile,
        "leaderboard": leaderboard,
    })

@login_required
def add_record(request):
    if request.method == "POST":
        form = CommuteRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            # Calculated emission (km/L formula)
            if record.fuel_efficiency > 0:
                fuel_consumed = record.distance / record.fuel_efficiency  # liters
                calculated_emission = fuel_consumed * 2.3  # kg CO2 per liter
            else:
                calculated_emission = 0.0
            record.predicted_emission = calculated_emission

            # ML model prediction
            predicted_emission_ml = None
            if model:
                # Prepare input for model (distance, fuel_efficiency, transport_mode_car)
                transport_mode_car = 1 if record.mode_of_transport.startswith('car') else 0
                try:
                    predicted_emission_ml = model.predict([[record.distance, record.fuel_efficiency, transport_mode_car]])[0]
                except Exception:
                    predicted_emission_ml = None
            record.save()

            # Update MonthlySummary
            from .models import MonthlySummary
            record_month = record.date.month
            record_year = record.date.year
            summary, created = MonthlySummary.objects.get_or_create(
                user=record.user,
                year=record_year,
                month=record_month,
                defaults={"total_emission": 0.0}
            )
            summary.total_emission += record.predicted_emission
            summary.save()

            # Store ML prediction in session for result view
            request.session['predicted_emission_ml'] = float(predicted_emission_ml) if predicted_emission_ml is not None else None
            request.session['calculated_emission'] = float(calculated_emission)
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

    # Get calculated and ML-predicted emissions from session
    calculated_emission = request.session.pop('calculated_emission', None)
    predicted_emission_ml = request.session.pop('predicted_emission_ml', None)
    return render(request, "tracker/result.html", {
        "record": record,
        "chart_path": f"/media/charts/chart_{record.id}.png",
        "calculated_emission": calculated_emission,
        "predicted_emission_ml": predicted_emission_ml,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_records(request):
    records = CommuteRecord.objects.filter(user=request.user).order_by('-date')
    serializer = CommuteRecordSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_predict(request):
    data = request.data
    distance = float(data.get('distance', 0))
    fuel_efficiency = float(data.get('fuel_efficiency', 0))
    mode_of_transport = data.get('mode_of_transport', '')
    weather = data.get('weather', 'clear')
    traffic_intensity = data.get('traffic_intensity', 'medium')
    road_type = data.get('road_type', 'city')
    # Calculated emission (km/L formula)
    if fuel_efficiency > 0:
        fuel_consumed = distance / fuel_efficiency
        calculated_emission = fuel_consumed * 2.3
    else:
        calculated_emission = 0.0
    # ML model prediction
    predicted_emission_ml = None
    error_margin = None
    if 'model' in globals() and model:
        import pandas as pd
        input_dict = {
            'distance': [distance],
            'fuel_efficiency': [fuel_efficiency],
            'transport_mode_car': [1 if mode_of_transport.startswith('car') else 0],
            'weather_rainy': [1 if weather == 'rainy' else 0],
            'weather_snowy': [1 if weather == 'snowy' else 0],
            'traffic_intensity_medium': [1 if traffic_intensity == 'medium' else 0],
            'traffic_intensity_high': [1 if traffic_intensity == 'high' else 0],
            'road_type_highway': [1 if road_type == 'highway' else 0],
        }
        X_input = pd.DataFrame(input_dict)
        try:
            predicted_emission_ml = model.predict(X_input)[0]
            # Dummy error margin (for demo, use model RMSE if available)
            error_margin = 0.5  # Replace with actual RMSE if tracked
        except Exception:
            predicted_emission_ml = None
    return Response({
        'calculated_emission': calculated_emission,
        'predicted_emission_ml': predicted_emission_ml,
        'error_margin': error_margin
    })
