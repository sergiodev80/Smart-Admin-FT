from unfold.settings import get_config
from unfold.utils import convert_color


def unfold_auth_context(request):
    """
    Context processor que proporciona las variables de Unfold
    para vistas de autenticación fuera del admin (password reset, etc.)
    """
    config = get_config("UNFOLD")

    colors = config.get("COLORS", {})
    for name, weights in colors.items():
        for weight, value in weights.items():
            colors[name][weight] = convert_color(value)

    return {
        "theme": config.get("THEME"),
        "colors": colors,
        "styles": config.get("STYLES", []),
        "scripts": config.get("SCRIPTS", []),
        "site_favicons": config.get("SITE_FAVICONS", []),
        "border_radius": config.get("BORDER_RADIUS"),
        "site_title": config.get("SITE_TITLE"),
        "site_header": config.get("SITE_HEADER"),
        "site_symbol": config.get("SITE_SYMBOL"),
    }
