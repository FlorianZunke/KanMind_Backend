from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsOwnerOrMember(BasePermission):
     def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()
     

class IsOwnerAndDeleteOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user == obj.owner
        return True
     
     
class TaskDetailPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return user == obj.board.owner or user in obj.board.members.all()

        elif request.method == 'PATCH':
            return user == obj.assigned_to or user == obj.reviewer

        elif request.method == 'DELETE':
            return user == obj.author or user == obj.board.owner

        return False