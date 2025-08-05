from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from kanban_app.models import Board, Comment, User, Task
from .serializers import BoardSerializer, BoardDetailReadSerializer, BoardDetailWriteSerializer, MiniUserSerializer, TaskSerializer, EmailCheckSerializer, TaskDetailSerializer, CommentSerializer
from .permissions import IsOwnerOrMember, IsAuthenticated, TaskDetailPermission, IsOwnerAndDeleteOnly, CommentPermission

class BoardViewSet(generics.ListCreateAPIView):
    """
    GET  /boards/   → List all boards the user owns or belongs to.
    POST /boards/   → Create a new board, automatically setting the request user as owner.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def get_queryset(self):
        """
        Return boards where the current user is either the owner or a member.
        """
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        """
        Save a new board instance with the current user as its owner.
        """
        serializer.save(owner=self.request.user)



class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /boards/<pk>/   → Retrieve a single board (403 if not owner or member).
    PATCH  /boards/<pk>/   → Update title or members (owner always preserved).
    PUT    /boards/<pk>/   → Same as PATCH.
    DELETE /boards/<pk>/   → Delete the board (only owner allowed).
    """
    permission_classes = [IsOwnerAndDeleteOnly, IsOwnerOrMember, IsAuthenticated]

    def get_object(self):
        """
        Fetch the board by PK and ensure the current user is owner or member.
        Raises PermissionDenied (403) if unauthorized.
        """
        board = get_object_or_404(Board, pk=self.kwargs['pk'])
        user = self.request.user
        if not (user == board.owner or user in board.members.all()):
            raise PermissionDenied("You are not allowed to access this board.")
        return board

    def get_serializer_class(self):
        """
        Select the read serializer for GET,
        and the write serializer (with owner_data & members_data) for PATCH/PUT.
        """
        if self.request.method in ('PATCH', 'PUT'):
            return BoardDetailWriteSerializer
        return BoardDetailReadSerializer
    

class CheckMailView(APIView):
    """
    GET /email-check/?email=<email>
    → Validate that the email exists, return the corresponding user's minimal data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Use the EmailCheckSerializer to validate the 'email' query parameter.
        Returns MiniUserSerializer data for the found user.
        """
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        data = MiniUserSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)
        
class TaskViewSet(generics.ListCreateAPIView):
    """
    GET  /tasks/   → List all tasks.
    POST /tasks/   → Create a new task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def get_serializer_context(self):
        """
        Inject the request into the serializer context for permission checks.
        """
        return {'request': self.request}
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /tasks/<pk>/   → Retrieve a single task.
    PATCH  /tasks/<pk>/   → Update a task.
    PUT    /tasks/<pk>/   → Replace a task.
    DELETE /tasks/<pk>/   → Delete a task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [TaskDetailPermission ,IsAuthenticated]

    def get_serializer_context(self):
        """
        Inject the request into the serializer context for field-level validation.
        """
        return {'request': self.request}

class AssignedDetailView(generics.ListAPIView):
    """
    GET /tasks/assigned-to-me/
    → List tasks where the current user is the assignee.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return tasks filtered by assigned_to == current user.
        """
        return Task.objects.filter(assigned_to=self.request.user)


class ReviewerDetailView(generics.ListAPIView):
    """
    GET /tasks/reviewing/
    → List tasks where the current user is the reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return tasks filtered by reviewer == current user.
        """
        return Task.objects.filter(reviewer=self.request.user)


class CommentViewSet(generics.ListCreateAPIView):
    """
    GET  /tasks/<task_id>/comments/   → List all comments for the task.
    POST /tasks/<task_id>/comments/   → Create a new comment on the task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure the user has board access, then return comments for the specified task.
        Raises PermissionDenied (403) if user is not a board member.
        """
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        user = self.request.user

        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return Comment.objects.filter(task=task).order_by('-created_at')

    def get_serializer_context(self):
        """
        Pass the 'task_id' into serializer context for create-time assignment.
        """
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_id')
        return context

class CommentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /tasks/<task_id>/comments/<comment_id>/   → Retrieve a single comment.
    DELETE /tasks/<task_id>/comments/<comment_id>/   → Delete the comment (only author).
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentPermission]

    def get_object(self):
        """
        Fetch the comment and ensure the user is either a board member (for GET)
        or the comment author (for DELETE). Raises PermissionDenied (403) otherwise.
        """
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        user = self.request.user

        if user != comment.task.board.owner and user not in comment.task.board.members.all():
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return comment