from django.urls import path, include
from .views import api_root, RegisterView, CustomLoginView, LogoutView, current_user
from rest_framework.routers import DefaultRouter
from .views import (
   UserSummaryViewSet, CustomLoginView, CustomUserViewSet, GroupViewSet ,SendFriendRequestView, AcceptFriendRequestView, ReceivedFriendRequestsView , DeleteFriendRequestView
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'groups', GroupViewSet)
user_summary = UserSummaryViewSet.as_view({'get': 'get_user_summary'})

urlpatterns = [
    path('', api_root, name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('current_user/', current_user, name='current-user'),
     path('user-summary/', user_summary, name='user-summary'),
    path('friend-request/send/<int:to_user_id>/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/accept/<int:request_id>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/received/', ReceivedFriendRequestsView.as_view(), name='received-friend-requests'),
     path('friend-request/delete/<int:request_id>/', DeleteFriendRequestView.as_view(), name='delete-friend-request'),
    path('', include(router.urls)),
]