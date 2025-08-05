from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Board(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='board_members')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_owner')

    def __str__(self):
        return self.title
    
    @property
    def member_count(self):
        return self.members.count()

    @property
    def ticket_count(self):
        return self.tasks.count()

    @property
    def tasks_to_do_count(self):
        return self.tasks.filter(status='todo').count()

    @property
    def tasks_high_prio_count(self):
        return self.tasks.filter(priority='high').count()



class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks_creater',
        null=False)

    def __str__(self):
      return self.title
    

class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)
