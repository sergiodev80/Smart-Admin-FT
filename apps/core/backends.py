from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import User


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.MultipleObjectsReturned:
            user = User.objects.filter(Q(username=username) | Q(email=username)).first()
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
