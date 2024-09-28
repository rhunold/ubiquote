import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight_search(text, search_query):
    if not search_query:
        return text
    escaped_query = re.escape(search_query)
    highlighted = re.sub(f'({escaped_query})', r'<strong>\1</strong>', text, flags=re.IGNORECASE)
    return mark_safe(highlighted)
