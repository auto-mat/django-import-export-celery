from django.db import models
from django.contrib.auth.models import User


class Winner(models.Model):
    name = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        default='',
    )
