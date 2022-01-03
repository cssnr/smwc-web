from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    return getattr(settings, value, None)


@register.filter(name='tag_to_class')
def tag_to_class(value):
    return {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
    }[value]
