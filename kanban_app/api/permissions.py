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
    """
    Permissions for tasks:
    - Can be read by all board members
    - Can only be edited by the rewiver and assignee
    - Can only be deleted by the task`s creator and the board owner
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return user == obj.board.owner or user in obj.board.members.all()

        elif request.method == 'PATCH':
            return user == obj.assigned_to or user == obj.reviewer

        elif request.method == 'DELETE':
            return user == obj.author or user == obj.board.owner

        return False
    
class CommentPermission(BasePermission):
    """
    Permissions for comments:
    - Can be read by all board members (including the board owner)
    - Can only be deleted by the comment's author
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return user == obj.task.board.owner or user in obj.task.board.members.all()

        elif request.method == 'DELETE':
            return user == obj.author

        return False