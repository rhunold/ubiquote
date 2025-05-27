# # yourapp/templatetags/quote_extras.py
from django import template

from django.utils.translation import get_language


register = template.Library()

@register.filter
def get_translated_title(category_dict):
    return category_dict.get(f"title_{get_language()}", category_dict.get("title"))

@register.filter
def get_translated_text(category_dict):
    return category_dict.get(f"text_{get_language()}", category_dict.get("text"))