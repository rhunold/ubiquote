# templatetags/my_filters.py
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def show_banner(context, absolute_index):
    user = context['user']
    divisor = 8 if user.is_authenticated else 4
    return absolute_index != 0 and absolute_index % divisor == 0