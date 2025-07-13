from django.db import models
from django.contrib.auth.models import User


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
        return self.tickets.count()

    @property
    def tasks_to_do_count(self):
        return self.tickets.filter(status='todo').count()

    @property
    def tasks_high_prio_count(self):
        return self.tickets.filter(priority='high').count()



class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    def __str__(self):
      return self.title

