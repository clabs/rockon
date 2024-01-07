from __future__ import annotations

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the band.
        if getattr(obj, "contact", None):
            return obj.contact == request.user
        if getattr(obj, "band", None):
            return obj.band.contact == request.user


class IsCrewReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow crew members to view the object.
    """

    def has_object_permission(self, request, view, obj):
        if (
            request.user.groups.filter(name="crew").exists()
            and request.method in permissions.SAFE_METHODS
        ):
            return True
