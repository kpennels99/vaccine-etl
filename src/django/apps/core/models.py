from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom User model. Email address is used for authentication."""

    email = models.EmailField('email address', unique=True)

    class Meta:
        """Override default meta attributes of User model."""

        ordering = ['-id']

    @property
    def is_admin(self):
        """Whether user has elevated privileges."""
        return self.is_staff or self.is_superuser
