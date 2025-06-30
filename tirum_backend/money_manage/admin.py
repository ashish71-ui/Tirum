from django.contrib import admin
from .models import (
    ExpenseCategory, Transaction, SplitDetail,
    KhataBookEntry, Notification, UtilityBillReminder, Wallet
)

admin.site.register(ExpenseCategory)
admin.site.register(Transaction)
admin.site.register(SplitDetail)
admin.site.register(KhataBookEntry)
admin.site.register(Notification)
admin.site.register(UtilityBillReminder)
admin.site.register(Wallet)