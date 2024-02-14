from django import template

register = template.Library()

@register.filter
def has_user_liked(liked_quotes, quote_id_or_bool):
    if isinstance(liked_quotes, dict):
        # Case for ListView: liked_quotes is a dictionary
        return liked_quotes.get(quote_id_or_bool, False)
    else:
        # Case for DetailView: liked_quotes is a boolean
        return liked_quotes