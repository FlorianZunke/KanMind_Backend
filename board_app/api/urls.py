from django.urls import path
from .views import BoardView


urlpatterns = [
    path('boards/', BoardView.as_view(), name='boards'),
    # path('boards/<int:pk>', BoardView.as_view(), name='board-detail'),
    # path('email-check/', BoardView.as_view(), name='email-check'),
]