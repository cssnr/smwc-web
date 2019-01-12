from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView

import home.views as home

app_name = 'home'


urlpatterns = [
    path('', home.home_view, name='index'),
    path('error/', home.error_view, name='error'),
    path('success/', home.success_view, name='success'),
    path('roms/', RedirectView.as_view(url='//roms.smwc.world/', permanent=False), name='roms'),
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.ico')), name='favicon'),
]
