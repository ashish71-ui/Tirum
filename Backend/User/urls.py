from django.urls import path
from .views import api_root, RegisterView, CustomLoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, GroupViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'groups', GroupViewSet)