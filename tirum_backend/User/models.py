from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    language = models.CharField(max_length=10, choices=[('en', 'English'), ('ne', 'Nepali')], default='en')
    friends = models.ManyToManyField('self', symmetrical=True, blank=True, related_name='user_friends')

class Group(models.Model):

    GROUP_TYPE_CHOICES = [
        ('FRIENDS', 'Friends'),
        ('FAMILY', 'Family'),
        ('BUSINESS', 'Business'),
        ('ROOMMATES', 'Roommates'),
        ('TRIP', 'Trip'),
        ('PARTY', 'Party'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='OTHER')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(CustomUser, related_name='user_groups')
    created_at = models.DateTimeField(auto_now_add=True)



class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')