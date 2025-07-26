from kanban_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer, MiniUserSerializer, TaskSerializer, EmailCheckSerializer, TaskDetailSerializer
from .permissions import IsOwnerOrMember, IsAuthenticated, IsAssignee, IsReviewer
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
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def delete(self, request, *args, **kwargs):
        board = self.get_object()

        if request.user != board.owner:
            return Response({"detail": "Nur der Besitzer darf dieses Board löschen."}, status=status.HTTP_403_FORBIDDEN)

        board.delete()
        return Response({"detail": "Das Board wurde erfolgreich gelöscht."}, status=status.HTTP_204_NO_CONTENT)
    

class CheckMailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = EmailCheckSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            data = MiniUserSerializer(user).data
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "E-Mail nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )
        

class TaskViewSet(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        board_id = data.get("board")
        if not board_id:
            return Response({"detail": "Board-ID fehlt."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        if not (user == board.owner or user in board.members.all()):
            return Response({"detail": "Zugriff verweigert. Du bist kein Mitglied dieses Boards."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    #Muss die Permission IsOwnerOrMember noch integrieren und brauche den ersteller des Tasks
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAssignee | IsReviewer ,IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()

        if request.user != task.reviewer:
            return Response({"detail": "Nur der Besitzer darf diesen Task löschen."}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response({"detail": "Der TAsk wurde erfolgreich gelöscht."}, status=status.HTTP_204_NO_CONTENT)

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
