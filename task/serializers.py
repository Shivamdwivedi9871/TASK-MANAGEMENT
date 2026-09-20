from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task

        fields = ['title', 'description', 'status', 'priority']

        read_only_fields = ['created_at', 'updated_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title could not be empty')

        return value
