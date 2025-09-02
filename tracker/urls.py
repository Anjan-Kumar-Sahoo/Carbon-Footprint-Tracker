from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("add_record/", views.add_record, name="add_record"),
    path("result/<int:record_id>/", views.result, name="result"),
    path("profile_settings/", views.profile_settings, name="profile_settings"),
    path("export_data/", views.export_data, name="export_data"),
    # API endpoints
    path("api/records/", views.api_records, name="api_records"),
    path("api/predict/", views.api_predict, name="api_predict"),
]
