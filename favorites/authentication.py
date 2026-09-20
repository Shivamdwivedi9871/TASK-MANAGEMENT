import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

User = get_user_model()


class CustomJwtAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_token = request.headers.get(
            "Authorization") or request.META.get("HTTP_AUTHORIZATION")

        if not auth_token:
            return None

        parts = auth_token.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed(
                "Inavlid Authorization format")

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token Expired")

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid Token")

        token_type = payload.get("type")
        if token_type not in ['access', 'refresh']:
            raise exceptions.AuthenticationFailed(
                "Inavlid Token provided")

        username = payload.get('username')

        if not username:
            raise exceptions.AuthenticationFailed("Token Missing username")

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("username not found")

        return (user, None)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
