from rest_framework.throttling import SimpleRateThrottle


class PerUserORIPThrottle(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):

        if request.user and request.user.is_authenticated:
            ident = f'user:{request.user.id}'

        else:
            ident = f"ip:{self.get_ident(request)}"

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
