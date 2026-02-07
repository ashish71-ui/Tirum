from rest_framework import serializers
from django.contrib.auth.models import User
from money_manage.models import Transaction
from .models import (CustomUser, Group,FriendRequest)
from decimal import Decimal

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
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    paid_by_username = serializers.CharField(source='paid_by.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False  # 👈 ensures JSON number, not string
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 
            'title', 
            'amount', 
            'transaction_type', 
            'date', 
            'created_at',
            'note',
            'mood',
            'category_name',
            'paid_by_username',
            'group_name'
        ]

class UserSummarySerializer(serializers.Serializer):
    """
    Serializer for user financial summary data
    """
    total_to_take = serializers.DecimalField(
    max_digits=10, decimal_places=2, coerce_to_string=False, default=Decimal("0.00")
    )
    total_to_return = serializers.DecimalField(
    max_digits=10, decimal_places=2, coerce_to_string=False, default=Decimal("0.00")
    )

    to_take_with = serializers.ListField(
        child=serializers.DictField()
    )
    to_return_with = serializers.ListField(
        child=serializers.DictField()
    )
    transactions = TransactionSerializer(many=True)