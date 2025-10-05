from __future__ import annotations

import uuid

from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from rockon.api.serializers import CommentSerializer
from rockon.bands.models import Comment


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated | permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Comment.objects.all()
        band_id = self.request.query_params.get('band', None)
        if band_id is not None:
            try:
                uuid.UUID(band_id)
            except ValueError:
                raise ValidationError('Invalid UUID format for band ID')
            queryset = queryset.filter(band__id=band_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
