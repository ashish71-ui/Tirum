from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ExpenseCategory, Transaction, SplitDetail,
    KhataBookEntry, Notification, UtilityBillReminder, Wallet
)

from User.models import (CustomUser, Group)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all(), required=False)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'phone_number', 'language', 'friends']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add a 'name' field that combines first_name and last_name, or falls back to username
        if instance.first_name and instance.last_name:
            data['name'] = f"{instance.first_name} {instance.last_name}"
        elif instance.first_name:
            data['name'] = instance.first_name
        else:
            data['name'] = instance.username
        return data

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class SplitDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SplitDetail
        fields = '__all__'

class KhataBookEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KhataBookEntry
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UtilityBillReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityBillReminder
        fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'