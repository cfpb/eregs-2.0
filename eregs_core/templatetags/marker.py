from django import template

register = template.Library()

@register.filter
def marker_type(marker_text):
    marker = marker_text.replace('(', '')
    marker = marker.replace(')', '')
    marker = marker.replace('.', '')
    return marker