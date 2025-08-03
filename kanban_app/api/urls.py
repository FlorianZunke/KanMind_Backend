from django.urls import path
from .views import BoardViewSet, BoardDetailView, CheckMailView, TaskViewSet, AssignedDetailView, ReviewerDetailView, TaskDetailView, CommentViewSet, CommentDetailView


urlpatterns = [
    path('boards/', BoardViewSet.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', CheckMailView.as_view(), name='email-check'),
    path('tasks/', TaskViewSet.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', AssignedDetailView.as_view(), name='assigned-to-me'),
    path('tasks/reviewing/', ReviewerDetailView.as_view(), name='rewiver-detail'),
    path('tasks/<int:task_id>/comments/', CommentViewSet.as_view(), name='comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
]