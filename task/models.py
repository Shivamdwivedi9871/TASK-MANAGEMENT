from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class Profile(models.Model):
    ROLE = [
        ('admin', 'Admin'),
        ('api_user', 'Api_User'),
        ('qa', 'Qa'),
        ('manager', 'Manager'),
        ('bucket', 'Bucket')
    ]
    role = models.CharField(max_length=50, choices=ROLE)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')


class Task(models.Model):
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('in-progress', 'In-Progress'),
        ('completed', 'Completed')
    ]

    PRIORITY_CHOICE = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('heigh', 'Heigh')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=40, choices=STATUS_CHOICE, default='pending')
    priority = models.CharField(
        max_length=40, choices=PRIORITY_CHOICE, default='medium')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='task')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
