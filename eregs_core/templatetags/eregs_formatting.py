import string

from django import template

register = template.Library()

@register.filter
def effective_date(date):
    date = date.split('-')
    if date[1][0] == '0':
        date[1] = date[1][1]
    if date[2][0] == '0':
        date[2] = date[2][1]

    return '/'.join([date[1], date[2], date[0]])

@register.filter
def lstrip(text):

    return string.lstrip(text)