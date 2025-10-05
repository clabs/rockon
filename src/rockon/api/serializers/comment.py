from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from rockon.bands.models import Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
