from django.urls import path 
from table import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/frame", views.analize, name="analyse")
]