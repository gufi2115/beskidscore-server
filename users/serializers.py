from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from users.models import UserM


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserM
        fields = ['id', 'username', 'email', 'role']


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserM
        fields = ['username', 'email', 'first_name', 'last_name','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        with transaction.atomic():
            user = UserM.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserM
        fields = ['username', 'email', 'first_name', 'last_name','password']
        extra_kwargs = {field: {'required': False} for field in fields}
    def update(self, instance, validated_data):
        with transaction.atomic():
            password = validated_data.pop('password', None)
            instance.set_password(password)
            super().update(instance, validated_data)
        return instance


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, write_only=True)
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect username or password')
