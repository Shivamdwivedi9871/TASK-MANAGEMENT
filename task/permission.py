from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.profile.role == 'admin':
            return True
        return obj.owner == request.user
