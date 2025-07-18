from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsOwnerOrMember(BasePermission):
     def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()