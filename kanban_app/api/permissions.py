from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsOwnerOrMember(BasePermission):
     def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()
     
     
class IsTaskAuthorOrBoardOwnerAndDeleteOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user == obj.author or request.user == obj.board.owner
        return True
        
     
class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user
    
class IsReviewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user