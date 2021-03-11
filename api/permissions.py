from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    """Permission class for user endpoints."""

    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission class for category and genre endpoints."""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return request.user.is_admin or request.user.is_staff


class IsModeratorOrOwnerOrReadOnly(permissions.BasePermission):
    """Permission class for review and comment endpoints."""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_staff
        )
