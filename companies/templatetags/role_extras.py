from django import template
register = template.Library()

@register.filter
def has_key(dict_obj, key):
    return key in dict_obj

@register.filter
def get_item(dict_obj, key):
    return dict_obj.get(key)
