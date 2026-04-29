from rest_framework import serializers
from money_manage.models import Transaction
from .models import (CustomUser, Group,FriendRequest)
from decimal import Decimal

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password_confirm', 'first_name', 'last_name', 'email', 'phone_number']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm', None)
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all(), required=False)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'avatar', 'avatar_url', 'language', 'friends']
        extra_kwargs = {
            'avatar': {'required': False},
            'friends': {'required': False},
        }

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url

class GroupMemberSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'name', 'email', 'avatar_url']
    def get_name(self, obj):
        return ' '.join(filter(None, [obj.first_name, obj.last_name])) or obj.username
    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url

class GroupSerializer(serializers.ModelSerializer):
    members_detail = GroupMemberSerializer(source='members', many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ['id', 'name', 'type', 'description', 'created_by', 'created_by_username',
                  'members', 'members_detail', 'member_count', 'created_at']
        extra_kwargs = {
            'members': {'required': False},
            'description': {'required': False, 'allow_blank': True},
        }
    def get_member_count(self, obj):
        return obj.members.count()

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
