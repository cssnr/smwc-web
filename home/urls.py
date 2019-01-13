from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView

import home.views as home

app_name = 'home'


urlpatterns = [
    path('', home.home_view, name='index'),
    path('roms/', home.roms_view, name='roms'),
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.ico')), name='favicon'),
]
