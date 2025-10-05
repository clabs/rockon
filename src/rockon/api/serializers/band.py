from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from rockon.bands.models import Band, BandMedia, BandVote, Track


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


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
            return UserSerializer(obj.contact).data
        return None


class BandListMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        # fields not listed here can not be changed via the API
        fields = [
            'file',
            'encoded_file',
        ]


class BandTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'


class BandListSerializer(serializers.ModelSerializer):
    # track = BandTrackSerializer(read_only=True, many=False)
    press_photo = BandListMediaSerializer(
        source='get_press_photo', read_only=True, many=False
    )
    bid_complete = serializers.ReadOnlyField()

    class Meta:
        model = Band
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = [
            'id',
            'guid',
            'name',
            'track',
            'bid_status',
            'federal_state',
            'are_students',
            'mean_age_under_27',
            'is_coverband',
            'bid_complete',
            'press_photo',
        ]


class BandDetailSerializer(serializers.ModelSerializer):
    # track = BandTrackSerializer(read_only=False, many=False)
    press_photo = BandListMediaSerializer(
        source='get_press_photo', read_only=True, many=False
    )
    logo = BandListMediaSerializer(source='get_logo', read_only=True, many=False)
    songs = BandMediaSerializer(source='get_songs', read_only=True, many=True)
    links = BandMediaSerializer(source='get_links', read_only=True, many=True)
    documents = BandMediaSerializer(source='get_documents', read_only=True, many=True)
    web_links = BandMediaSerializer(source='get_web_links', read_only=True, many=True)
    contact = UserSerializer(read_only=True)

    class Meta:
        model = Band
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = '__all__'


class BandVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandVote
        # fields not listed here can not be changed via the API
        fields = ['band', 'user', 'vote']
