from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("add_record/", views.add_record, name="add_record"),
    path("result/<int:record_id>/", views.result, name="result"),
]

