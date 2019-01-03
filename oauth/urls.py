from django.urls import path

import oauth.views as oauth

app_name = 'oauth'


urlpatterns = [
    path('', oauth.do_oauth, name='login'),
    path('logout/', oauth.log_out, name='logout'),
    path('callback/', oauth.callback, name='callback'),
]
