from django.contrib import admin
from home.models import Webhooks


@admin.register(Webhooks)
class WebhooksAdmin(admin.ModelAdmin):
    list_per_page = 500
    list_display = ('owner_username', 'hook_id', 'active')
