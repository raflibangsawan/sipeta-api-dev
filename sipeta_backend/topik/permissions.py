from rest_framework import permissions


class IsTopikUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user) and (request.user == view.topik.created_by))
