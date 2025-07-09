from django.urls import path
from .views import BoardView


urlpatterns = [
    path('boards/', BoardView, name='boards'),
    path('boards/<int:pk>', BoardView, name='board-detail'),
    path('email-check/', BoardView, name='email-check'),
]