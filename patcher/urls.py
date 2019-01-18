from django.urls import path

import patcher.views as view

app_name = 'patcher'

urlpatterns = [
    path('', view.rom_patcher, name='index'),
]
