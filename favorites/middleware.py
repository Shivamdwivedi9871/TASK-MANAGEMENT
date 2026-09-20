import logging
import time
import uuid
import os
import redis
from django.http import JsonResponse
from django.conf import settings
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL)


class RequestIdMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request_id = str(uuid.uuid4)

        request.request_id = request_id

        response = self.get_response(request)

        response["X-Request_id"] = request_id

        return response


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        method = request.method
        path = request.path
        request_id = getattr(request, "request_id", None)

        response = self.get_response(request)

        print("Response:", type(response))

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # ms
        user = getattr(request, "user", None)
        user_id = getattr(
            user, "id", None) if user and user.is_authenticated else "Anonymous"

        status = getattr(response, "status_code", None)

        logger.info(
            f"reuest_id = {request_id}, user={user_id}, method={method}, path={path}"
            f"status={status}, duration_ms = {duration:.2f}"
        )

        return response


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        self.limit = 60
        self.window_seconds = 60

    def __call__(self, request):

        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            identifier = f"user:{request.user.id}"

        else:
            identifier = f"ip:{request.META.get('REMOTE_ADDR')}"

        key = f"rate:{identifier}"

        count = redis_client.incr(key)

        if count == 1:
            redis_client.expire(key, self.window_seconds)

        if count > self.limit:
            return JsonResponse({
                "details": "Too Many Request"
            }, status=429)

        response = self.get_response(request)
        return response
