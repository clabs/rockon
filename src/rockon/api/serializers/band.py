from __future__ import annotations

from rest_framework import serializers

from rockon.bands.models import Band, BandMedia, Track, track


class BandTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = "__all__"


class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        track = BandTrackSerializer
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = [
            "id",
            "name",
            "has_management",
            "are_students",
            "genre",
            "federal_state",
            "homepage",
            "facebook",
            "cover_letter",
            "contact",
            "track",
            "techrider",
            "updated_at",
        ]


class BandMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        # fields not listed here can not be changed via the API
        fields = [
            "id",
            "band",
            "media_type",
            "url",
            "file",
            "thumbnail",
            "file_name_original",
        ]
