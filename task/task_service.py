from .models import Task
from rest_framework.response import Response


class TaskService:
    @staticmethod
    def create_task(user, validated_data):
        if Task.objects.filter(owner=user, task=validated_data.get('title', '')).exists():
            return Response('Task already created')
        task = Task.objects.create(owner=user, **validated_data)
        return Response({
            'message': 'Task Created',
            'data': task
        })
