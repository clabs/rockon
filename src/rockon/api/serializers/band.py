from __future__ import annotations

from rest_framework import serializers

from rockon.bands.models import BandMedia, Track


class BandMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        # fields not listed here can not be changed via the API
        fields = '__all__'

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
        fields = '__all__'
