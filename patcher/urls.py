from django.urls import path

import patcher.views as view

app_name = 'patcher'

urlpatterns = [
    path('', view.show_patcher, name='index'),
    path('testing/', view.test_view, name='test_view'),
]
