from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Group
User = get_user_model()
# Create your models here.
class Event(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']


class FAQ(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_date']
