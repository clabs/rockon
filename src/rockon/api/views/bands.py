from __future__ import annotations

from ast import parse

from rest_framework import permissions, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from rockon.api.permissions import IsOwner
from rockon.api.serializers import BandMediaSerializer, BandSerializer
from rockon.bands.models import Band, BandMedia


class BandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Band.objects.all()
    serializer_class = BandSerializer
    permission_classes = [permissions.IsAdminUser | IsOwner]


class BandMediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows media files belong to a band to be viewed or edited.
    """

    serializer_class = BandMediaSerializer
    permission_classes = [permissions.IsAdminUser | IsOwner]

    @action(detail=False, methods=["get"])
    def get_queryset(self):
        media = BandMedia.objects.all()
        if self.request.query_params.get("band_id", None):
            media = media.filter(band__id=self.request.query_params.get("band_id"))
        if not self.request.user.is_staff:
            media.filter(band=self.request.user.band)
        return media

    @action(detail=False, methods=["post"], url_path="upload", url_name="upload")
    @parser_classes(
        [
            MultiPartParser,
        ]
    )
    def perform_create(self, drf_request, *args, **kwargs):
        serializer = self.get_serializer(data=drf_request.data)
        serializer.is_valid(raise_exception=True)
        band = serializer.validated_data.get("band")
        user = self.request.user
        if not band.id == user.band.id and not user.is_staff:
            raise PermissionError("You can only upload media for your own band.")
        serializer.save()
        return Response(serializer.data, status=201)
