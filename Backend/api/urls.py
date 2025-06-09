from django.urls import path
from .views import api_root, RegisterView, CustomLoginView, LogoutView

urlpatterns = [
    path('', api_root, name='api-root'),  #  root index
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
