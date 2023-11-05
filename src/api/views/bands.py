from __future__ import annotations

from rest_framework import permissions, viewsets

from api.permissions import IsOwner
from api.serializers import BandSerializer
from bands.models import Band


class BandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Band.objects.all()
    serializer_class = BandSerializer
    permission_classes = [permissions.IsAdminUser, IsOwner]
