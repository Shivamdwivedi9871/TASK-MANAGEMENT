import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings


def create_access_token(user):
    now = datetime.now(timezone.utc)

    access_exp = now + timedelta(minutes=settings.JWT_TOKEN_EXPIRATION)

    payload = {
        'username': user.username,
        'exp': access_exp,
        'iat': now,
        'type': 'access'
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY,
                       algorithm=settings.JWT_ALGORITHM)

    return token


def create_refresh_token(user):
    now = datetime.now(timezone.utc)

    refresh_exp = now + timedelta(days=settings.JWT_REFRESH_TOKEN_LIFETIME)

    payload = {
        'username': user.username,
        'exp': refresh_exp,
        'iat': now,
        'type': 'refresh'
    }

    refresh_token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return refresh_token
