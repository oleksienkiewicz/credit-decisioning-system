from django.urls import path

from . import views

urlpatterns = [
    path('', views.application_create, name="application_create"),
    path('applications/<int:pk>/', views.application_detail, name="application_detail"),
]