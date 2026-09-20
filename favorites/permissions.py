from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user

        if user and user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return True

        return getattr(obj, 'owner', None) == request.user
