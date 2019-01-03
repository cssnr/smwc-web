from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name='get_config')
def get_config(section, value, fallback=None):
    return settings.CONFIG.get(section, value, fallback=fallback)
