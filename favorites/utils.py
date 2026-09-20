import jwt
from django.conf import settings
from rest_framework import exceptions


def decode_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Token Expired')

    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Inavlid Token')
