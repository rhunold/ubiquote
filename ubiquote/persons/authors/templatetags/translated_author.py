from django import template
from django.utils.translation import get_language

register = template.Library()

@register.filter
def translated_name(author):
    # Get the current language code
    current_language = get_language()

    # Check if the current language exists in the translated_name dictionary
    if 'translated_name' in author and current_language in author['translated_name']:
        return author['translated_name'][current_language]

    # Fallback to the fullname if no translation is available for the current language
    return author['fullname']
