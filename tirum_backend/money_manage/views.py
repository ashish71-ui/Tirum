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

class UserSummaryViewSet(viewsets.ModelViewSet):
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
