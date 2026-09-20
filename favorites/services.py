from django.db import transaction
from .models import Favorite, categories
from django.contrib.auth import get_user_model
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379,
                           db=0, decode_responses=True)
User = get_user_model()


class CreateType:

    def create_category(user, favorite_data, category):

        with transaction.atomic():
            favorite = Favorite.objects.create(
                title=favorite_data.get('title', ""),
                author=favorite_data.get('author', ""),
                rating=favorite_data.get('rating', 1),
                owner=user,
            )

            category = categories.objects.create(
                favorites=favorite,
                type=category.get('type', "")
            )
        return favorite


class CustomRateLimit:

    @staticmethod
    def check_rate_limit(user_id, limit=60, window_seconds=60):

        key = f"rate:user:{user_id}"

        count = redis_client.incr(key)

        if count == 1:
            redis_client.expire(key, window_seconds)

        if count > limit:
            return False

        else:
            return True

    @staticmethod
    def get_user_profile(user_id: int) -> dict:

        key = f"user:{user_id}"

        profile = redis_client.hgetall(key)

        if profile:
            return profile

        user = User.objects.get(pk=id)

        profile = {
            "user_id": str(user.id),
            "username": str(user.username),
            "email": getattr(user, "email", ""),
            "is_staff": str(getattr(user, "is_staff", False))
        }

        redis_client.hset(key, mapping=profile)

        redis_client.expire(key, 86400)

        return profile

    @staticmethod
    def update_user_address(user_id: int, new_Address: str) -> None:

        key = f"user:{user_id}"

        user = User.objects.get(pk=id)

        user.profile.address = new_Address
        user.profile.save()

        redis_client.hset(key, "address", new_Address)
        redis_client.expire(key, 86400)

    @staticmethod
    def has_liked(post_id: int, user_id: int) -> bool:
        key = f"post:{post_id}:likes"

        is_memeber = redis_client.sismember(key, str(user_id))
        return bool(is_memeber)

    @staticmethod
    def is_liked(post_id: int, user_id: int) -> None:

        key = f"post:{post_id}:likes"

        redis_client.sadd(key, str(user_id))

    @staticmethod
    def unlike_post(post_id: int, user_id: int) -> None:
        key = f"post:{post_id}:likes"

        redis_client.srem(key, str(user_id))

    @staticmethod
    def toggele_post(post_id: int, user_id: int) -> None:

        key = f"post:{post_id}:likes"

        already_liked = redis_client.sismember(key, str(user_id))

        if already_liked:
            redis_client.srem(key, str(user_id))
            liked_count = redis_client.scard(key)

            return {
                "action": "Unliked",
                "liked_count": liked_count
            }

        else:
            redis_client.sadd(key, str(user_id))
            liked_count = redis_client.scard(key)

            return {
                "action": "liked",
                "liked_count": liked_count
            }


EMAIL_QUEUE = 'queue:emails'
DLQ = 'queue:emails:failed'
PROCESSING_QUEUE = 'queue:email:claims'
MAX_RETRIES = 3


def send_email_redis(user_email, job):
    redis_client.rpush(EMAIL_QUEUE, json.dumps(job))

    raw_job = redis_client.lpop(EMAIL_QUEUE)

    if raw_job is None:
        return None

    try:
        job = json.loads(raw_job)
        email = job.get('email')

        if not email:
            raise ValueError('Email Not Found')

        raise RuntimeError('Email Provider Unavailable')

    except ValueError as error:
        job['error'] = str(error)
        job['failure_type'] = 'Permanent'

        redis_client.rpush(DLQ, json.dumps(job),)
        print("Permanent Failure: Job Moved to DLQ")

    except RuntimeError as error:
        job['retries'] += 1
        job['error'] = str(error)
        job['failure_types'] = 'Temporery'

        if job['retries'] >= MAX_RETRIES:
            redis_client.rpush(DLQ, json.dumps(job),)
            print('Job Moved to DLQ')

        else:
            redis_client.rpush(EMAIL_QUEUE, json.dumps(job),)
            print(
                f'Job sent back to email queue with retries {job['retries']}')

    def replay_dlq_jobs():

        while True:
            raw_job = redis_client.lpop(DLQ)

            job = json.loads(raw_job)

            job['retries'] = 0
            job.pop('error', None)
            job.pop('failure_types', None)

            redis_client.lmove(DLQ, EMAIL_QUEUE, "LEFT", "RIGHT")

    def claim_email_job(user_email):
        raw_job = redis_client.lmove(
            EMAIL_QUEUE, PROCESSING_QUEUE, 'RIGHT', 'LEFT')

        if not raw_job:
            return None
        return raw_job

    def acknowledge_job(raw_job):
        job = json.loads(raw_job)

        try:
            email = job.get('email', None)

            if not email:
                raise ValueError("Email Not Found")

            print(f"Sending email to {email}")

            print("Email sent successfully")

            redis_client.lrem(PROCESSING_QUEUE, 1, raw_job,)

        except ValueError as error:
            job['error'] = str(error)
            job['failure_type'] = 'Permananet'

            redis_client.lrem(PROCESSING_QUEUE, 1, raw_job,)

            redis_client.rpush(DLQ, json.dumps(job),)

            print("Invalid Job Move to DLQ")

        except RuntimeError as error:
            job['retries'] += 1
            job['error'] = str(error)
            job['failure_type'] = 'Temporery'

            if job['retries'] >= MAX_RETRIES:
                redis_client.lrem(PROCESSING_QUEUE, 1, raw_job,)

                redis_client.rpush(DLQ, json.dumps(job))

                print("Job move to DLQ")

            else:
                redis_client.lrem(PROCESSING_QUEUE, 1, raw_job,)
                redis_client.rpush(EMAIL_QUEUE, json.dumps(job))
                print(
                    f"Sent back to email queue with retries {job['retries']}")
