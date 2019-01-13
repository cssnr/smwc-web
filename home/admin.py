from django.contrib import admin
from home.models import Hacks, Webhooks


@admin.register(Webhooks)
class WebhooksAdmin(admin.ModelAdmin):
    list_display = ('owner_username', 'hook_id', 'active')


@admin.register(Hacks)
class HacksAdmin(admin.ModelAdmin):
    list_display = ('smwc_id', 'name', 'smwc_href', 'demo', 'featured')
