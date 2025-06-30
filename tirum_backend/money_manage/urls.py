from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseCategoryViewSet, TransactionViewSet, SplitDetailViewSet,
    KhataBookEntryViewSet, NotificationViewSet, UtilityBillReminderViewSet,
    WalletViewSet, UserSummaryViewSet, test_cors
)

router = DefaultRouter()
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'split-details', SplitDetailViewSet)
router.register(r'khata-entries', KhataBookEntryViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'bill-reminders', UtilityBillReminderViewSet)
router.register(r'wallets', WalletViewSet)
router.register(r'user-summary', UserSummaryViewSet, basename='user-summary')

urlpatterns = [
    path('test_cors/', test_cors, name='test-cors'),
    path('', include(router.urls)),
]