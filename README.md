# Carbon Footprint Tracker

## Project Story

Climate change is one of the most pressing issues of our time. I built this project to help individuals track, analyze, and reduce their personal carbon emissions from daily commutes. By combining Django, machine learning, and engaging analytics, users can make informed choices and see their environmental impact in real time.

## Tech Stack & Features

- **Backend:** Django 5, Django REST Framework
- **Frontend:** Bootstrap 5, custom templates
- **Database:** SQLite (default, easy to swap)
- **Machine Learning:** scikit-learn (regression model, confidence intervals)
- **Features:**
  - Add commute records (mode, distance, fuel, weather, traffic, road type)
  - ML-powered emission predictions
  - Analytics dashboard (charts, progress bars, leaderboard)
  - Badges for eco achievements
  - Export data (CSV/PDF)
  - REST API for mobile/external integrations
  - Weekly email reports (Celery)

## Demo Screenshots & Live Link

---

## Installation Steps

1. **Clone the repo:**
   ```
   git clone https://github.com/yourusername/carbon_footprint_tracker.git
   cd carbon_footprint_tracker
   ```
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Run migrations:**
   ```
   python manage.py migrate
   ```
4. **Train the ML model:**
   ```
   python tracker/ml_model/train_model.py
   ```
5. **Start the server:**
   ```
   python manage.py runserver
   ```
6. **Login and explore:**
   - Add commute records
   - View analytics dashboard
   - Try the API endpoints (`/api/records/`, `/api/predict/`)

## Contact
