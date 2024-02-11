from __future__ import annotations

from rest_framework import serializers

from rockon.bands.models import Band, BandMedia, BandVote, Track


class BandMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        # fields not listed here can not be changed via the API
        fields = "__all__"


class BandListMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandMedia
        # fields not listed here can not be changed via the API
        fields = [
            "file",
            "encoded_file",
        ]


class BandTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = "__all__"


class BandListSerializer(serializers.ModelSerializer):
    # track = BandTrackSerializer(read_only=True, many=False)
    press_photo = BandListMediaSerializer(
        source="get_press_photo", read_only=True, many=False
    )
    bid_complete = serializers.ReadOnlyField()

    class Meta:
        model = Band
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = [
            "id",
            "guid",
            "name",
            "track",
            "federal_state",
            "are_students",
            "bid_complete",
            "press_photo",
        ]


class BandDetailSerializer(serializers.ModelSerializer):
    # track = BandTrackSerializer(read_only=False, many=False)
    press_photo = BandListMediaSerializer(
        source="get_press_photo", read_only=True, many=False
    )
    logo = BandListMediaSerializer(source="get_logo", read_only=True, many=False)
    songs = BandMediaSerializer(source="get_songs", read_only=True, many=True)
    links = BandMediaSerializer(source="get_links", read_only=True, many=True)
    documents = BandMediaSerializer(source="get_documents", read_only=True, many=True)

    class Meta:
        model = Band
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = "__all__"

    # def update(self, instance, validated_data):
    #     # print(self, instance, validated_data)
    #     track_data = validated_data.pop("track")
    #     print(track_data)
    #     instance.track = track_data
    #     instance.save()
    #     return instance


class BandVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandVote
        # fields not listed here can not be changed via the API
        fields = ["band", "user", "vote"]
