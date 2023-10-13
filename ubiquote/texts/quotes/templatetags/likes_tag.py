from django import template

register = template.Library()

@register.filter
def has_user_liked(liked_quotes, quote_id):
    return liked_quotes.get(quote_id, False)