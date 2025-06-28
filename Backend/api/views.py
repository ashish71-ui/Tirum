from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, action
from rest_framework.reverse import reverse
from django.contrib.auth import logout
from .serializers import RegisterSerializer, CustomUserSerializer
from rest_framework import viewsets
from .models import (
    ExpenseCategory, Transaction, SplitDetail,
    KhataBookEntry, Notification, UtilityBillReminder, Wallet
)
from User.models import (CustomUser, Group)

from .serializers import (
    CustomUserSerializer, GroupSerializer, ExpenseCategorySerializer, TransactionSerializer,
    SplitDetailSerializer, KhataBookEntrySerializer, NotificationSerializer, UtilityBillReminderSerializer, WalletSerializer
)
from django.db import models

# Test endpoint for CORS
@api_view(['GET'])
def test_cors(request):
    return Response({'message': 'CORS is working!', 'status': 'success'})

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
    print(f"Current user view called. User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"Request headers: {dict(request.headers)}")
    
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
        'test_cors': reverse('test_cors', request=request, format=format),
    })

# Basic ModelViewSets for all main models
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

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class SplitDetailViewSet(viewsets.ModelViewSet):
    queryset = SplitDetail.objects.all()
    serializer_class = SplitDetailSerializer

class KhataBookEntryViewSet(viewsets.ModelViewSet):
    queryset = KhataBookEntry.objects.all()
    serializer_class = KhataBookEntrySerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class UtilityBillReminderViewSet(viewsets.ModelViewSet):
    queryset = UtilityBillReminder.objects.all()
    serializer_class = UtilityBillReminderSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class UserSummaryViewSet(viewsets.ViewSet):
    """
    Returns a summary for a user: total money to take, total money to return, with whom, and all transaction details.
    """
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        user = request.user
        # Total money to take (user is lender, not settled)
        to_take = KhataBookEntry.objects.filter(lender=user, is_settled=False)
        to_return = KhataBookEntry.objects.filter(borrower=user, is_settled=False)
        # With whom
        to_take_with = to_take.values('borrower__username').annotate(total=models.Sum('amount'))
        to_return_with = to_return.values('lender__username').annotate(total=models.Sum('amount'))
        # All transactions
        transactions = Transaction.objects.filter(paid_by=user) | Transaction.objects.filter(splits__user=user)
        transactions = transactions.distinct()
        transaction_data = TransactionSerializer(transactions, many=True).data
        return Response({
            'total_to_take': sum([entry.amount for entry in to_take]),
            'total_to_return': sum([entry.amount for entry in to_return]),
            'to_take_with': list(to_take_with),
            'to_return_with': list(to_return_with),
            'transactions': transaction_data,
        })

###########  Logic for Backend calculation 
