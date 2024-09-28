from django import template

register = template.Library()

# print("get_item")

@register.filter(name='get_item')
def get_item(dictionary, key):
    # print(dictionary)
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''  # Return an empty string if the dictionary is invalid