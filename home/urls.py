from django.urls import path

import home.views as home

app_name = 'home'


urlpatterns = [
    path('', home.home_view, name='index'),
    path('error/', home.error_view, name='error'),
    path('success/', home.success_view, name='success'),
]
