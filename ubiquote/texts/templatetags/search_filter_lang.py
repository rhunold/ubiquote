
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def build_query(get_params, keys=None):
    """
    Builds a query string from GET parameters.
    Optionally filter which keys to include (as a comma-separated string).
    """
    keys = keys.split(",") if keys else get_params.keys()
    params = []

    for key in keys:
        values = get_params.getlist(key)
        for val in values:
            params.append((key, val))

    return "&" + urlencode(params)