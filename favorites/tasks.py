from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from celery.utils.log import get_task_logger
from .models import Favorite, User

logger = get_task_logger(__name__)


@shared_task
def notification_email(to_email):
    subject = "You have added Book"
    message = "Hey You have added Book in your favorite table"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        fail_silently=False
    )


@shared_task
def test_task():
    print('Celery is working')
    return 'Celery is working'


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 3},
)
def send_daily_favorite(user_id):
    user = User.objects.get(id=user_id)
    favorites = Favorite.objects.filter(owner=user)
    title = ','.join(favorite.title for favorite in favorites)

    message = (
        f"Hello {user.username}, \n\n"
        f"Your favorites: {title or 'No Favorite yet'}"
    )
    sent_count = send_mail(
        subject="Daily Task Schedule",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['your_email@mail.com'],
        fail_silently=False
    )

    return f"Daily Email Favorite Queued {user.id}; sent={sent_count}"


'''Temporary Failure'''


@shared_task(bind=True, max_retries=3)
def retry_demo(self):
    try:
        raise ConnectionError('Email Provider is temporary unavailable')
    except ConnectionError as exc:
        logger.warning('Temporay provider failure: retrying task_id = %s',
                       self.request.id,)
        raise self.retry(exc=exc, countdown=5)


''''Permanent Failure'''


@shared_task(bind=True, max_retries=3)
def no_retry_demo(self, mode='temporary'):
    try:
        if mode == 'temporary':
            raise ConnectionError('Email Provider is temporary unavailable')
        elif mode == 'permanent':
            raise ValueError('Inavlid Email Payload')

        return 'Task Succeeded'
    except ConnectionError as exc:
        logger.warning('Temporay provider failure: retrying task_id = %s',
                       self.request.id,)
        raise self.retry(exc=exc, countdown=5)

    except ValueError as exc:
        logger.error(
            'Permanent Failure; no retry task_id=%s error=%s',
            self.request.id,
            exc,
        )

        raise
