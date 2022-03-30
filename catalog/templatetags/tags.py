from django import template

register = template.Library()


@register.filter(name='xrange')
def xrange(number):
    return range(1, number+1)
