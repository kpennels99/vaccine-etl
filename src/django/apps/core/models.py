"""Core model definitions."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model. Email address is used for authentication."""

    email = models.EmailField('email address', unique=True)

    class Meta:
        """Override default meta attributes of User model."""

        ordering = ['-id']
