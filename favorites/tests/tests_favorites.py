import pytest
from rest_framework.test import APIClient
from favorites.models import Favorite, User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user_instance, _ = User.objects.get_or_create(username="testuser")
    return user_instance


@pytest.mark.django_db
def test_successfull_favorite_creation(api_client, user):
    api_client.force_authenticate(user=user)

    payload = {
        # "id": 1,
        "title": "django-run",
        "author": user,
        "rating": 5
    }

    response = api_client.post("/v1/books/", data=payload)

    assert response.status_code == 201
