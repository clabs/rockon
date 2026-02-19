from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from rockon.api.permissions import IsOwner
from rockon.api.serializers import (
    BandMediaSerializer,
    BandTrackSerializer,
)
from rockon.bands.models import BandMedia, Track


class BandMediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows media files belong to a band to be viewed or edited.
    """

    serializer_class = BandMediaSerializer
    permission_classes = [permissions.IsAdminUser | IsOwner]

    @action(detail=False, methods=['get'])
    def get_queryset(self):
        media = BandMedia.objects.select_related('band').all()
        if self.request.query_params.get('band_id', None):
            media = media.filter(band__id=self.request.query_params.get('band_id'))
        if not self.request.user.is_staff:
            user_bands = self.request.user.bands.values_list('id', flat=True)
            media = media.filter(band__id__in=user_bands)
        return media

    @action(detail=False, methods=['post'], url_path='upload', url_name='upload')
    @parser_classes(
        [
            MultiPartParser,
        ]
    )
    def perform_create(self, drf_request, *args, **kwargs):
        serializer = self.get_serializer(data=drf_request.data)
        serializer.is_valid(raise_exception=True)
        band = serializer.validated_data.get('band')
        user = self.request.user
        if not user.bands.filter(id=band.id).exists() and not user.is_staff:
            raise PermissionError('You can only upload media for your own band.')
        serializer.save()
        serializer.instance.encode_file()  # non-blocking: errors logged inside
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BandTrackViewSet(viewsets.ModelViewSet):
    serializer_class = BandTrackSerializer

    def get_queryset(self):
        queryset = Track.objects.all().filter(active=True)
        event_slug = self.request.query_params.get('event', None)
        if event_slug is not None:
            queryset = queryset.filter(events__slug__icontains=event_slug)
        return queryset
