from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        null=False,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        related_name='recipe_fans'
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='shoppers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username'
            )
        ]
