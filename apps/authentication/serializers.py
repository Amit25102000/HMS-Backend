"""
Serializers for Authentication app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    password = serializers.CharField(write_only=True, required=False)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'address', 'profile_picture',
            'is_active', 'created_at', 'groups', 'permissions', 'password'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_groups(self, obj):
        """Return user's group names"""
        return [group.name for group in obj.groups.all()]
    
    def get_permissions(self, obj):
        """Return user's permissions"""
        # Get all permissions (from groups and user-specific)
        perms = obj.get_all_permissions()
        return list(perms)
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
