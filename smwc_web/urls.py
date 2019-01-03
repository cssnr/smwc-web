from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('home.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('debug/', include(debug_toolbar.urls))] + urlpatterns
