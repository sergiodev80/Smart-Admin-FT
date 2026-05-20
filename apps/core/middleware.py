from django.conf import settings


class CookieLanguageMiddleware:
    """Si el usuario ya eligió idioma via cookie, forzarlo ignorando Accept-Language."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if cookie_lang:
            request.META["HTTP_ACCEPT_LANGUAGE"] = cookie_lang
        return self.get_response(request)
