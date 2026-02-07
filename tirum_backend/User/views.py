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
from .models import FriendRequest
from .serializers import FriendRequestSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics, permissions, status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from money_manage.models import KhataBookEntry, SplitDetail, Transaction
from .serializers import UserSummarySerializer
from django.db.models import Sum, Q
from decimal import Decimal

User = get_user_model()


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

        if response.status_code != 200:
            return response  # handles 400 errors for invalid credentials

        token = response.data['token']
        user = Token.objects.get(key=token).user
        user_serializer = CustomUserSerializer(user)

        return Response({
            'token': token,
            'user': user_serializer.data,
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

    @action(detail=False, methods=['post'], url_path='add-friend')
    def add_friend(self, request):
        user = request.user
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if friend == user:
            return Response({'error': 'You cannot add yourself as a friend.'}, status=status.HTTP_400_BAD_REQUEST)

        if friend in user.friends.all():
            return Response({'error': 'User is already your friend.'}, status=status.HTTP_400_BAD_REQUEST)

        user.friends.add(friend)
        user.save()
        return Response({'status': f'{friend.username} added as a friend.'})

    @action(detail=False, methods=['get'], url_path='my-friends')
    def list_my_friends(self, request):
        """Return current user's friends as full objects (id, username, email, name)."""
        friends = request.user.friends.all().order_by('username')
        serializer = CustomUserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search-users')
    def search_users(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'users': []})

        users = CustomUser.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)[:10]  # Limit to 10 results, exclude self

        serializer = CustomUserSerializer(users, many=True)
        return Response({'users': serializer.data})

    @action(detail=False, methods=['post'], url_path='create-friend')
    def create_friend(self, request):
        """
        Create a new user account and add them as a friend
        """
        data = request.data
        username = data.get('username')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new user
        try:
            # Generate a random password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))
    
            new_user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            # Add as friend
            request.user.friends.add(new_user)

            serializer = CustomUserSerializer(new_user)
            return Response({
                'message': f'Friend {username} created and added successfully.',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Failed to create friend: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user = User.objects.get(pk=kwargs['to_user_id'])
        friend_request, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user
        )
        if not created:
            return Response({'detail': 'Friend request already sent'}, status=400)

        # Send real-time notification
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     f"user_{to_user.id}",
        #     {
        #         'type': 'friend_request',
        #         'message': f"{request.user.username} sent you a friend request."
        #     }
        # )
        return Response(FriendRequestSerializer(friend_request).data, status=201)

# Accept request
class AcceptFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        friend_request = FriendRequest.objects.get(pk=kwargs['request_id'])

        if friend_request.to_user != request.user:
            return Response({'detail': 'Not authorized'}, status=403)

        if friend_request.is_accepted:
            return Response({'detail': 'Friend request already accepted.'}, status=400)

        friend_request.is_accepted = True
        friend_request.save()

        # Add each other as friends
        request.user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(request.user)
        request.user.save()
        friend_request.from_user.save()

        return Response({'detail': 'Friend request accepted.'}, status=200)

# List received friend requests
class ReceivedFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, is_accepted=False)


class DeleteFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, request_id, *args, **kwargs):
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=404)

        # Only sender or receiver can delete the request
        if request.user != friend_request.from_user and request.user != friend_request.to_user:
            return Response({"detail": "Not authorized to delete this request."}, status=403)

        friend_request.delete()
        return Response({"detail": "Friend request deleted."}, status=204)





class UserSummaryViewSet(viewsets.ViewSet):
    """
    ViewSet for user financial summary operations
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='summary')
    def get_user_summary(self, request):
        """
        Get comprehensive financial summary for the authenticated user
        """
        user = request.user
        
        try:
            # Calculate amounts user needs to take (money owed to user)
            to_take_data = self._calculate_to_take_amounts(user)
            total_to_take = sum(item['total'] for item in to_take_data)
            
            # Calculate amounts user needs to return (money user owes)
            to_return_data = self._calculate_to_return_amounts(user)
            total_to_return = sum(item['total'] for item in to_return_data)
            
            # Get recent transactions
            recent_transactions = self._get_recent_transactions(user)
            
            # Prepare response data - convert Decimal to float for JSON serialization
            summary_data = {
                'total_to_take': float(total_to_take),
                'total_to_return': float(total_to_return),
                'to_take_with': to_take_data,
                'to_return_with': to_return_data,
                'transactions': recent_transactions
            }
            
            # Return data directly to preserve nested structures
            return Response(summary_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch user summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_to_take_amounts(self, user):
        """
        Calculate money that others owe to the current user with detailed transaction info
        """
        to_take_dict = {}
        
        # From KhataBook entries where user is the lender
        khata_entries = KhataBookEntry.objects.filter(
            lender=user,
            is_settled=False
        ).select_related('borrower')
        
        for entry in khata_entries:
            username = entry.borrower.username
            if username not in to_take_dict:
                to_take_dict[username] = {
                    'borrower__username': username,
                    'total': 0,
                    'transactions': []
                }
            to_take_dict[username]['total'] += float(entry.amount)
            to_take_dict[username]['transactions'].append({
                'type': 'khata',
                'id': entry.id,
                'title': entry.reason,
                'amount': float(entry.amount),
                'date': entry.created_at.isoformat(),
            })
        
        # From split transactions where others owe money to user
        split_details = SplitDetail.objects.filter(
            transaction__paid_by=user,
            is_paid=False
        ).exclude(
            user=user  # Exclude user's own split
        ).select_related('transaction', 'user', 'transaction__category')
        
        for split in split_details:
            username = split.user.username
            if username not in to_take_dict:
                to_take_dict[username] = {
                    'borrower__username': username,
                    'total': 0,
                    'transactions': []
                }
            to_take_dict[username]['total'] += float(split.amount)
            to_take_dict[username]['transactions'].append({
                'type': 'expense',
                'id': split.transaction.id,
                'title': split.transaction.title,
                'amount': float(split.amount),
                'date': split.transaction.created_at.isoformat(),
                'category': split.transaction.category.name if split.transaction.category else 'General',
            })
        
        return sorted(to_take_dict.values(), key=lambda x: x['total'], reverse=True)

    def _calculate_to_return_amounts(self, user):
        """
        Calculate money that the current user owes to others with detailed transaction info
        """
        to_return_dict = {}
        
        # From KhataBook entries where user is the borrower
        khata_entries = KhataBookEntry.objects.filter(
            borrower=user,
            is_settled=False
        ).select_related('lender')
        
        for entry in khata_entries:
            username = entry.lender.username
            if username not in to_return_dict:
                to_return_dict[username] = {
                    'lender__username': username,
                    'total': 0,
                    'transactions': []
                }
            to_return_dict[username]['total'] += float(entry.amount)
            to_return_dict[username]['transactions'].append({
                'type': 'khata',
                'id': entry.id,
                'title': entry.reason,
                'amount': float(entry.amount),
                'date': entry.created_at.isoformat(),
            })
        
        # From split transactions where user owes money (PAYMENT REQUESTS)
        split_details = SplitDetail.objects.filter(
            user=user,
            is_paid=False
        ).exclude(
            transaction__paid_by=user  # Exclude transactions user paid for
        ).select_related('transaction', 'transaction__paid_by', 'transaction__category')
        
        for split in split_details:
            username = split.transaction.paid_by.username
            if username not in to_return_dict:
                to_return_dict[username] = {
                    'lender__username': username,
                    'total': 0,
                    'transactions': []
                }
            to_return_dict[username]['total'] += float(split.amount)
            to_return_dict[username]['transactions'].append({
                'type': 'expense',
                'id': split.transaction.id,
                'split_id': split.id,
                'title': split.transaction.title,
                'amount': float(split.amount),
                'date': split.transaction.created_at.isoformat(),
                'category': split.transaction.category.name if split.transaction.category else 'General',
                'note': split.transaction.note or '',
            })
        
        return sorted(to_return_dict.values(), key=lambda x: x['total'], reverse=True)

    def _get_recent_transactions(self, user, limit=20):
        """
        Get recent transactions for the user
        """
        # Get transactions where user is involved (either paid or has a split)
        user_transactions = Transaction.objects.filter(
            Q(paid_by=user) | Q(splits__user=user)
        ).distinct().select_related(
            'category', 'paid_by', 'group'
        ).prefetch_related(
            'splits', 'splits__user'
        ).order_by('-created_at')[:limit]
        
        # Serialize transactions with split details
        transaction_data = []
        for tx in user_transactions:
            tx_dict = {
                'id': tx.id,
                'title': tx.title,
                'amount': float(tx.amount),
                'transaction_type': tx.transaction_type,
                'date': tx.date.isoformat() if tx.date else None,
                'created_at': tx.created_at.isoformat(),
                'note': tx.note or '',
                'mood': tx.mood or '',
                'category_name': tx.category.name if tx.category else 'General',
                'paid_by_username': tx.paid_by.username,
                'paid_by_id': tx.paid_by.id,
                'group_name': tx.group.name if tx.group else None,
                'splits': []
            }
            
            # Add split details
            for split in tx.splits.all():
                tx_dict['splits'].append({
                    'id': split.id,
                    'user_id': split.user.id,
                    'user_username': split.user.username,
                    'amount': float(split.amount),
                    'is_paid': split.is_paid,
                    'paid_at': split.paid_at.isoformat() if split.paid_at else None,
                })
            
            transaction_data.append(tx_dict)
        
        return transaction_data

    @action(detail=False, methods=['get'], url_path='khata-summary')
    def get_khata_summary(self, request):
        """
        Get detailed khata book summary
        """
        user = request.user
        
        try:
            # Active lending (money others owe to user)
            active_lendings = KhataBookEntry.objects.filter(
                lender=user,
                is_settled=False
            ).select_related('borrower').order_by('-created_at')
            
            # Active borrowings (money user owes to others)
            active_borrowings = KhataBookEntry.objects.filter(
                borrower=user,
                is_settled=False
            ).select_related('lender').order_by('-created_at')
            
            # Recent settled transactions
            recent_settled = KhataBookEntry.objects.filter(
                Q(lender=user) | Q(borrower=user),
                is_settled=True
            ).select_related('lender', 'borrower').order_by('-settled_at')[:10]
            
            lending_data = []
            for entry in active_lendings:
                lending_data.append({
                    'id': entry.id,
                    'borrower_username': entry.borrower.username,
                    'amount': float(entry.amount),
                    'reason': entry.reason,
                    'created_at': entry.created_at,
                })
            
            borrowing_data = []
            for entry in active_borrowings:
                borrowing_data.append({
                    'id': entry.id,
                    'lender_username': entry.lender.username,
                    'amount': float(entry.amount),
                    'reason': entry.reason,
                    'created_at': entry.created_at,
                })
            
            settled_data = []
            for entry in recent_settled:
                settled_data.append({
                    'id': entry.id,
                    'lender_username': entry.lender.username,
                    'borrower_username': entry.borrower.username,
                    'amount': float(entry.amount),
                    'reason': entry.reason,
                    'settled_at': entry.settled_at,
                })
            
            return Response({
                'active_lendings': lending_data,
                'active_borrowings': borrowing_data,
                'recent_settled': settled_data,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch khata summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='split-summary')
    def get_split_summary(self, request):
        """
        Get summary of split transactions
        """
        user = request.user
        
        try:
            # Money others owe from splits (user paid, others haven't)
            money_owed_to_user = SplitDetail.objects.filter(
                transaction__paid_by=user,
                is_paid=False
            ).exclude(user=user).values(
                'user__username'
            ).annotate(
                total_owed=Sum('amount')
            ).order_by('-total_owed')
            
            # Money user owes from splits (others paid, user hasn't)
            money_user_owes = SplitDetail.objects.filter(
                user=user,
                is_paid=False
            ).exclude(
                transaction__paid_by=user
            ).values(
                'transaction__paid_by__username'
            ).annotate(
                total_owed=Sum('amount')
            ).order_by('-total_owed')
            
            return Response({
                'money_owed_to_user': list(money_owed_to_user),
                'money_user_owes': list(money_user_owes),
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch split summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
