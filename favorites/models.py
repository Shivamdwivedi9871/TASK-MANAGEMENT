from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Favorite(models.Model):
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        indexes = [
            models.Index(
                fields=['title', 'author'],
                include=['rating'],

                name="idx_favorite_title_author_cove"
            ),
        ]

    def __str__(self):
        return f'{self.title}'


class categories(models. Model):
    favorites = models.ForeignKey(
        Favorite, on_delete=models.CASCADE, related_name='category')
    type = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type
