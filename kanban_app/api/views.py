from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from kanban_app.models import Board, Comment, User, Task
from .serializers import BoardSerializer, BoardDetailSerializer, MiniUserSerializer, TaskSerializer, EmailCheckSerializer, TaskDetailSerializer, CommentSerializer
from .permissions import IsOwnerOrMember, IsAuthenticated, TaskDetailPermission, IsOwnerAndDeleteOnly, CommentPermission

class BoardViewSet(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardDetailSerializer
    permission_classes = [IsOwnerAndDeleteOnly, IsOwnerOrMember, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        owner = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owner | member).distinct()

    def get_serializer_context(self):
        return {'request': self.request}
    

class CheckMailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        data = MiniUserSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)
        
class TaskViewSet(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [TaskDetailPermission ,IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

class AssignedDetailView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


class ReviewerDetailView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class CommentViewSet(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        user = self.request.user

        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return Comment.objects.filter(task=task).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_id')
        return context

class CommentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentPermission]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        user = self.request.user

        if user != comment.task.board.owner and user not in comment.task.board.members.all():
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")

        return comment