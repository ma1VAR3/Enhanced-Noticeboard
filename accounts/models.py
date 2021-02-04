from django.conf import settings
from django.contrib.auth import get_user_model
from django import template
from django.db import models
from django.utils.text import slugify

User = get_user_model()
register = template.Library()

class Group(models.Model):
    admin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(allow_unicode=True, unique=True)
    members = models.ManyToManyField(User,through='GroupMember')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

class GroupMember(models.Model):
    group = models.ForeignKey(Group,related_name="memberships",on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name="user_groups",on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ("group","user")
