from django.urls import path
from .views import TaskCreateView, TaskDetailView

urlpatterns = [
    path("tasks/", TaskCreateView.as_view(), name='task-list-create'),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name='task-details'),
]
