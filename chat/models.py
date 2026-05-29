from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class MyChats(models.Model):

    me = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='its_me'
    )

    frnd = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='my_friend'
    )

    chats = models.JSONField(default=dict)