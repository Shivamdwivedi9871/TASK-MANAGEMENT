from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .task_service import TaskService
from .permission import IsOwnerOrAdmin

# Create your views here.


class TaskCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.select_related('user').all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        task = TaskService.create_task(
            self.request.user, serializer.validated_data)
        serializer.instance = task


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
