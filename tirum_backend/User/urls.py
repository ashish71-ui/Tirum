from django.urls import path, include
from .views import api_root, RegisterView, CustomLoginView, LogoutView, current_user
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, GroupViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('current_user/', current_user, name='current-user'),
    path('', include(router.urls)),
]