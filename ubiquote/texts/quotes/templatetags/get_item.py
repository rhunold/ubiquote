from django import template

register = template.Library()

# print("get_item")

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, '')