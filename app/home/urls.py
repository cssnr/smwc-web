from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('roms/', views.roms_view, name='roms'),
]
