from __future__ import annotations

from rest_framework import serializers

from bands.models import Band


class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        # fields not listed here can not be changed via the API
        # FIXME: needs auth + permissions
        fields = [
            "name",
            "has_management",
            "are_students",
            "genre",
            "federal_state",
            "homepage",
            "facebook",
            "cover_letter",
            "contact",
            "techrider",
        ]
