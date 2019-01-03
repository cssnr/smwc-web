from django.urls import path
from django.views.generic.base import RedirectView

import home.views as home

app_name = 'home'


urlpatterns = [
    path('', home.home_view, name='index'),
    path('roms/', RedirectView.as_view(url='//roms.smwc.world/', permanent=False), name='roms'),
    path('error/', home.error_view, name='error'),
    path('success/', home.success_view, name='success'),
]
