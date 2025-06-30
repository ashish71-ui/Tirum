from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, action
from rest_framework.reverse import reverse
from django.contrib.auth import logout
from .serializers import RegisterSerializer, CustomUserSerializer, GroupSerializer
from rest_framework import viewsets
from .models import (CustomUser, Group)
from django.db import models

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=201)
        return Response(serializer.errors, status=400)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        user = Token.objects.get(key=token).user
        user_serializer = CustomUserSerializer(user)
        return Response({
            'token': token,
            'user': user_serializer.data
        })

class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=200)

@api_view(['GET'])
def current_user(request):
    """Get current authenticated user information"""
    if request.user.is_authenticated:
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'Not authenticated'}, status=401)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'logout': reverse('logout', request=request, format=format),
    })

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post'], url_path='add-friend')
    def add_friend(self, request, pk=None):
        user = request.user
        try:
            friend = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if friend == user:
            return Response({'error': 'You cannot add yourself as a friend.'}, status=status.HTTP_400_BAD_REQUEST)
        user.friends.add(friend)
        user.save()
        return Response({'status': f'{friend.username} added as a friend.'})

    @action(detail=True, methods=['post'], url_path='remove-friend')
    def remove_friend(self, request, pk=None):
        user = request.user
        try:
            friend = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.friends.remove(friend)
        user.save()
        return Response({'status': f'{friend.username} removed from friends.'})

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        members = data.pop('members', [])
        # Only allow friends as members
        friend_ids = set(request.user.friends.values_list('id', flat=True))
        if members:
            invalid = [uid for uid in members if int(uid) not in friend_ids and int(uid) != request.user.id]
            if invalid:
                return Response({'error': 'You can only add your friends as group members.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        # Add members if provided
        if members:
            group.members.set(members)
        else:
            group.members.add(request.user)
        group.save()
        out_serializer = self.get_serializer(group)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)