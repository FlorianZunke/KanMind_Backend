from board_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsOwnerOrMember
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics





class BoardView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrMember]


    
