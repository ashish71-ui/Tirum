from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    language = models.CharField(max_length=10, choices=[('en', 'English'), ('ne', 'Nepali')], default='en')
    friends = models.ManyToManyField('self', symmetrical=True, blank=True, related_name='user_friends')

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(CustomUser, related_name='user_groups')
    created_at = models.DateTimeField(auto_now_add=True)