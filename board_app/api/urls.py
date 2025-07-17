from django.urls import path
from .views import BoardViewSet, BoardDetailView


urlpatterns = [
    path('boards/', BoardViewSet.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    # path('email-check/', BoardView.as_view(), name='email-check'),
]