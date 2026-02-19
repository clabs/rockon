from __future__ import annotations

from rest_framework import serializers

from rockon.bands.models import BandMedia, Track


class BandMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        fields = [
            'id',
            'band',
            'media_type',
            'url',
            'file',
            'encoded_file',
            'file_name_original',
            'thumbnail',
            'created_at',
            'updated_at',
        ]

    # only booking team can see contact
    def get_contact(self, obj):
        request = self.context.get('request')
        if (
            request
            and request.user
            and request.user.groups.filter(name='booking').exists()
        ):
            from django.contrib.auth.models import User
            from rest_framework import serializers as s

            class UserSerializer(s.ModelSerializer):
                class Meta:
                    model = User
                    fields = ['id', 'username', 'email', 'first_name', 'last_name']

            return UserSerializer(obj.contact).data
        return None


class BandTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'name', 'slug', 'active', 'events']
