from django.urls import path

from . import views

app_name = 'patcher'

urlpatterns = [
    path('', views.patcher_view, name='home'),
]
