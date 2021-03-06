from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include('home.urls')),
    path('patcher/', include('patcher.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('discord/', RedirectView.as_view(url=settings.APP_DISCORD_INVITE)),
    path('flower/', RedirectView.as_view(url='/flower/'), name='flower'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('debug/', include(debug_toolbar.urls))] + urlpatterns
