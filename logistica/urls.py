from django.urls import path

from . import views

app_name = "logistica"

urlpatterns = [
    path("", views.index, name="index"),
    path("thresholds/", views.threshold_list, name="thresholds"),
]
