from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsBoss(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.username.upper() == 'A133982' and request.method in permissions.SAFE_METHODS
