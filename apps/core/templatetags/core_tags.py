from django import template

register = template.Library()


@register.filter
def make_range(value):
    """Convierte un entero N en range(N) para iterar N veces en templates."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)
