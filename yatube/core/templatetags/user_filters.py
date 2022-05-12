from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Регистрация фильтра."""
    return field.as_widget(attrs={'class': css})
