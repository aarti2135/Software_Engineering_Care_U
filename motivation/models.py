from django.db import models
from django.contrib.auth.models import User


class Avatar(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="avatars/")

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, null=True, blank=True,
                               on_delete=models.SET_NULL)

    def __str__(self):
        return f"Profile for {self.user.username}"
