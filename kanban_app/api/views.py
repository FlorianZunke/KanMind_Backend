from kanban_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer, MiniUserSerializer, TaskSerializer, EmailCheckSerializer, TaskDetailSerializer
from .permissions import IsOwnerOrMember, IsAuthenticated, IsAssignee, IsReviewer, IsTaskAuthorOrBoardOwnerAndDeleteOnly
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..models import User, Task
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


    
class BoardViewSet(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsTaskAuthorOrBoardOwnerAndDeleteOnly, IsOwnerOrMember, IsAuthenticated]

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
    permission_classes = [IsAssignee | IsReviewer | IsTaskAuthorOrBoardOwnerAndDeleteOnly ,IsAuthenticated]

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
