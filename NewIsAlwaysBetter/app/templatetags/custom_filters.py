from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def mul(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
        
@register.filter
def subtract(value, arg):
    """Soustrait l'argument de la valeur"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
