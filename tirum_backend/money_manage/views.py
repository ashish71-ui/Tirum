from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action
from .models import (
    ExpenseCategory, Transaction, SplitDetail,
    KhataBookEntry, Notification, UtilityBillReminder, Wallet
)
from .serializers import (
    ExpenseCategorySerializer, TransactionSerializer,
    SplitDetailSerializer, KhataBookEntrySerializer, NotificationSerializer, UtilityBillReminderSerializer, WalletSerializer
)
from django.db import models
from rest_framework import viewsets
from django.db import transaction as db_transaction
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from User.models import CustomUser

# Test endpoint for CORS
@api_view(['GET'])
def test_cors(request):
    return Response({'message': 'CORS is working!', 'status': 'success'})

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        splits_data = validated_data.pop('splits')
        paid_by_user = validated_data['paid_by']
        total_amount = float(validated_data['amount'])

        with db_transaction.atomic():
            # Save transaction first
            transaction = Transaction.objects.create(**validated_data)

            total_split = 0
            for split in splits_data:
                user = split['user']
                amount = float(split['amount'])
                total_split += amount

                is_paid = (user.id == paid_by_user.id)
                paid_at = datetime.now() if is_paid else None

                SplitDetail.objects.create(
                    transaction=transaction,
                    user=user,
                    amount=amount,
                    is_paid=is_paid,
                    paid_at=paid_at
                )

            if round(total_split, 2) != round(total_amount, 2):
                return Response(
                    {"error": "Split amounts do not match the total transaction amount."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(self.get_serializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='create-expense')
    def create_expense(self, request):
        """
        Create an expense transaction with automatic splitting among friends.
        Supports both equal and custom splitting.
        """
        user = request.user
        data = request.data

        # Required fields
        title = data.get('title')
        amount = data.get('amount')
        friends = data.get('friends', [])  # List of usernames
        split_type = data.get('split_type', 'equal')  # 'equal' or 'custom'

        if not title or not amount or not friends:
            return Response(
                {'error': 'Title, amount, and friends are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate users exist and are friends (can only split with friends)
        user_friends = set(user.friends.values_list('id', flat=True))
        friend_objects = []
        for friend_username in friends:
            try:
                friend = CustomUser.objects.get(username=friend_username)
                # Check if friend is in user's friends list
                if friend.id not in user_friends:
                    return Response(
                        {'error': f'User {friend_username} is not your friend. Please send a friend request first.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                friend_objects.append(friend)
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': f'User {friend_username} not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Get or create default category
        category = ExpenseCategory.objects.filter(name='General').first()
        if not category:
            category = ExpenseCategory.objects.create(name='General')

        # Prepare splits
        splits = []
        if split_type == 'equal':
            # Include the user who paid in the split
            total_participants = len(friend_objects) + 1  # friends + user
            split_amount = round(amount / total_participants, 2)

            # Add user (who paid)
            splits.append({
                'user': user,
                'amount': split_amount,
                'is_paid': True,
                'paid_at': datetime.now()
            })

            # Add friends
            for friend in friend_objects:
                splits.append({
                    'user': friend,
                    'amount': split_amount,
                    'is_paid': False,
                    'paid_at': None
                })

        elif split_type == 'custom':
            custom_splits = data.get('custom_splits', [])
            if len(custom_splits) != len(friend_objects) + 1:
                return Response(
                    {'error': 'Custom splits must include amounts for all participants (including yourself).'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_split = 0
            # Add user split
            user_split = next((s for s in custom_splits if s.get('username') == user.username), None)
            if not user_split:
                return Response(
                    {'error': 'Custom splits must include an amount for yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            splits.append({
                'user': user,
                'amount': float(user_split['amount']),
                'is_paid': True,
                'paid_at': datetime.now()
            })
            total_split += float(user_split['amount'])

            # Add friend splits
            for friend in friend_objects:
                friend_split = next((s for s in custom_splits if s.get('username') == friend.username), None)
                if not friend_split:
                    return Response(
                        {'error': f'Custom splits must include an amount for {friend.username}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                split_amount = float(friend_split['amount'])
                splits.append({
                    'user': friend,
                    'amount': split_amount,
                    'is_paid': False,
                    'paid_at': None
                })
                total_split += split_amount

            if round(total_split, 2) != round(amount, 2):
                return Response(
                    {'error': 'Custom split amounts do not match the total amount.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'error': 'Invalid split_type. Must be "equal" or "custom".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create transaction
        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                title=title,
                amount=amount,
                category=category,
                transaction_type='personal',  # Could be 'group' if we add group support later
                paid_by=user,
                note=data.get('note', ''),
                mood=data.get('mood', '')
            )

            # Create split details
            for split in splits:
                SplitDetail.objects.create(
                    transaction=transaction,
                    user=split['user'],
                    amount=split['amount'],
                    is_paid=split['is_paid'],
                    paid_at=split['paid_at']
                )

        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='create-group-expense')
    def create_group_expense(self, request):
        user = request.user
        data = request.data
        title = data.get('title')
        amount = data.get('amount')
        group_id = data.get('group_id')
        split_type = data.get('split_type', 'equal')

        if not title or not amount or not group_id:
            return Response({'error': 'Title, amount, and group_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)

        from User.models import Group
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not group.members.filter(id=user.id).exists():
            return Response({'error': 'You are not a member of this group.'}, status=status.HTTP_403_FORBIDDEN)

        members = list(group.members.all())
        category = ExpenseCategory.objects.filter(name='General').first()
        if not category:
            category = ExpenseCategory.objects.create(name='General')

        splits = []
        if split_type == 'equal':
            n = len(members)
            base = round(amount / n, 2)
            remainder = round(amount - base * n, 2)
            for i, member in enumerate(members):
                splits.append({
                    'user': member,
                    'amount': base + (remainder if i == 0 else 0),
                    'is_paid': member.id == user.id,
                    'paid_at': datetime.now() if member.id == user.id else None,
                })

        elif split_type == 'custom':
            custom_splits = data.get('custom_splits', [])
            member_map = {m.id: m for m in members}
            assigned_ids = set()
            total_split = 0.0
            for cs in custom_splits:
                uid = cs.get('user_id')
                amt = cs.get('amount')
                if not uid or amt is None:
                    return Response({'error': 'Each custom split needs user_id and amount.'}, status=status.HTTP_400_BAD_REQUEST)
                uid = int(uid)
                if uid not in member_map:
                    return Response({'error': f'User {uid} is not a group member.'}, status=status.HTTP_400_BAD_REQUEST)
                splits.append({
                    'user': member_map[uid],
                    'amount': float(amt),
                    'is_paid': uid == user.id,
                    'paid_at': datetime.now() if uid == user.id else None,
                })
                total_split += float(amt)
                assigned_ids.add(uid)
            missing = set(member_map.keys()) - assigned_ids
            if missing:
                return Response({'error': 'All group members must have a split amount.'}, status=status.HTTP_400_BAD_REQUEST)
            if round(total_split, 2) != round(amount, 2):
                return Response({'error': f'Split total ({total_split:.2f}) must equal expense amount ({amount:.2f}).'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid split_type. Must be "equal" or "custom".'}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                title=title, amount=amount, category=category,
                transaction_type='group', paid_by=user, group=group,
                note=data.get('note', ''),
            )
            for split in splits:
                SplitDetail.objects.create(
                    transaction=transaction, user=split['user'],
                    amount=split['amount'], is_paid=split['is_paid'], paid_at=split['paid_at'],
                )

        return Response(self.get_serializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='close')
    def close_transaction(self, request, pk=None):
        transaction = self.get_object()
        if transaction.paid_by != request.user:
            return Response(
                {'error': 'Only the payer can close this transaction.'},
                status=status.HTTP_403_FORBIDDEN
            )
        transaction.splits.filter(is_paid=False).update(
            is_paid=True, paid_at=datetime.now()
        )
        return Response({'status': 'Transaction closed. All splits marked as settled.'})


class SplitDetailViewSet(viewsets.ModelViewSet):
    queryset = SplitDetail.objects.all()
    serializer_class = SplitDetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """
        Mark a split detail as paid (settle payment)
        """
        split_detail = self.get_object()
        
        # Only the user who owes money can mark it as paid
        if split_detail.user != request.user:
            return Response(
                {'error': 'You can only mark your own payments as paid.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if split_detail.is_paid:
            return Response(
                {'error': 'This payment is already marked as paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        split_detail.is_paid = True
        split_detail.paid_at = datetime.now()
        split_detail.save()
        
        serializer = self.get_serializer(split_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

###########  Logic for tirum_backend calculation 
