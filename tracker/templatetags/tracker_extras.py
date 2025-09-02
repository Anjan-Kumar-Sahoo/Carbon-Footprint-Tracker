from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def get_suggestions(suggestions_dict, record_id):
    """Get suggestions for a specific record ID"""
    return suggestions_dict.get(record_id, {})
