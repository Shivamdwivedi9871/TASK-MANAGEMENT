from rest_framework import serializers
from .models import Favorite, categories


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    # author = serializers.SlugRelatedField(slug_field='owner', read_only=True)

    class Meta:
        model = Favorite

        fields = ['id', 'title', 'author', 'rating', 'owner']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating should be between 1 to 5')
        return value

    def validate(self, data):
        title = data.get('title', '')
        author = data.get('author', None)

        author_name = author.username if hasattr(
            author, 'username') else str(author)

        if title and author and title.lower().strip() == author_name.lower():
            raise serializers.ValidationError(
                'Title and Author should not be same')
        return data


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = categories

        fields = ['favorite', 'type']

        read_only_fields = ['created_at', 'updated_at']

    def validate_type(self, value):
        if value and value.lower().strip() == '':
            raise serializers.ValidationError("Type can't be null")

        return value
