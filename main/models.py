from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    host        = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    topic       = models.ForeignKey(Topic, null=True, on_delete=models.SET_NULL)
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    updated     = models.DateTimeField(auto_now=True)
    created     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    room        = models.ForeignKey(Room, on_delete=models.CASCADE)
    body        = models.TextField()   
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body[0:50]
    
    class Meta:
        ordering = ['-updated', '-created']



