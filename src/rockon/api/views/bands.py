from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from rockon.api.permissions import IsCrewReadOnly, IsOwner
from rockon.api.serializers import (
    BandDetailSerializer,
    BandListSerializer,
    BandMediaSerializer,
    BandTrackSerializer,
    BandVoteSerializer,
)
from rockon.bands.models import Band, BandMedia, BandVote, Track
from rockon.base.models import Event


class BandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Band.objects.all()
    permission_classes = [IsCrewReadOnly | permissions.IsAdminUser | IsOwner]

    def get_serializer_class(self):
        if self.action == "list":
            return BandListSerializer
        return BandDetailSerializer

    def get_queryset(self):
        queryset = Band.objects.all()
        event_slug = self.request.query_params.get("event", None)
        if event_slug is not None:
            queryset = queryset.filter(event__slug=event_slug)
        return queryset


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
        serializer.instance.encode_file()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BandVoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows votes to be viewed or edited.
    """

    serializer_class = BandVoteSerializer
    permission_classes = [permissions.IsAdminUser | IsOwner]
    http_method_names = ["get", "patch", "delete"]

    def retrieve(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_404_NOT_FOUND)
        all_votes = BandVote.objects.filter(user=request.user)
        band_id = kwargs.get("pk", None)
        if band_id:
            vote = get_object_or_404(all_votes, band__id=band_id)
            serializer = self.get_serializer(vote)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return BandVote.objects.none()
        all_votes = BandVote.objects.filter(user=self.request.user)
        band_id = self.kwargs.get("pk", None)
        if band_id:
            vote = all_votes.filter(band__id=band_id, user=self.request.user)
            return vote
        return all_votes

    @action(detail=False, methods=["patch"])
    def perform_create(self, drf_request):
        try:
            band_id = drf_request.data.get("band")
            band = Band.objects.get(id=band_id)
            user = self.request.user
            vote = drf_request.data.get("vote")
            if vote == -1:
                BandVote.objects.filter(band=band, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            vote = BandVote.objects.update_or_create(
                band=band, user=user, defaults={"vote": vote, "event": band.event}
            )
        except (KeyError, BandVote.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_201_CREATED)


class BandTrackViewSet(viewsets.ModelViewSet):
    serializer_class = BandTrackSerializer

    def get_queryset(self):
        queryset = Track.objects.all().filter(active=True)
        event_slug = self.request.query_params.get("event", None)
        if event_slug is not None:
            queryset = queryset.filter(events__slug__icontains=event_slug)
        return queryset
