from django.urls import path
from .views import api_root, RegisterView, CustomLoginView, LogoutView, test_cors, current_user
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseCategoryViewSet, TransactionViewSet,
    SplitDetailViewSet, KhataBookEntryViewSet, NotificationViewSet, UtilityBillReminderViewSet, WalletViewSet,
    UserSummaryViewSet
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
    path('', api_root, name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', current_user, name='current_user'),
    path('test-cors/', test_cors, name='test_cors'),
]

urlpatterns += router.urls