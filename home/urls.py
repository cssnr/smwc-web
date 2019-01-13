from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView

import home.views as home

app_name = 'home'


urlpatterns = [
    path('', home.home_view, name='index'),
    path('roms/', home.roms_view, name='roms'),
    path('error/', home.error_view, name='error'),
    path('flower/', RedirectView.as_view(url='//flower.smwc.world/'), name='flower'),
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.ico')), name='favicon'),
]
