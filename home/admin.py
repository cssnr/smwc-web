from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from home.models import Webhooks


@admin.register(Webhooks)
class WebhooksAdmin(admin.ModelAdmin):
    list_per_page = 500
    list_display = ('owner_username', 'hook_id', 'active')
    # fieldsets = (
    #     (None, {
    #         'fields': ('username', 'status', 'title', 'description', 'datetime', 'duration', 'rt', 'impact',
    #                    'work_type', 'cm_type', 'stakeholders', 'acted_on_by', 'action_taken', 'acted_on_at')
    #     }),
    #     ('Additional options', {
    #         'classes': ('collapse',),
    #         'fields': ('reminder_duration', 'calendar_reminder', 'calendar_invite_id', 'slack_message', 'color'),
    #     }),
    # )
    #
    # def show_title(self, obj):
    #     url_string = '<a href="{0}/change/">{1}</a>'
    #     return format_html(url_string.format(obj.id, obj.title))
    # show_title.short_description = 'Title'
    # show_title.admin_order_field = 'title'
    #
    # def show_rt(self, obj):
    #     url_string = '<a href="{0}/Ticket/Display.html?id={1}" target="_blank">{1}</a>'
    #     return format_html(url_string.format(settings.RT_HOST, obj.rt))
    # show_rt.short_description = 'RT'
    # show_rt.admin_order_field = 'rt'
    #
    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
