from django.contrib import admin
from .models import Favorite, categories
# Register your models here.


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'rating',
        'owner'
    )


# @admin.register(Author)
# class AuthorAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#     )

@admin.register(categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('type',)
