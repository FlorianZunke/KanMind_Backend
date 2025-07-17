from board_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsOwnerOrMember, IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
from rest_framework import viewsets




    
class BoardViewSet(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrMember, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer