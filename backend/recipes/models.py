from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
    )
    units = models.CharField(
        max_length=20,
        null=False,
        blank=False
    )


class Tag(models.Model):
    name = models.CharField(
        max_length=25,
        null=False,
        blank=False,
        unique=True
    )
    color = models.CharField(
        max_length=6,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET('Gordon Ramsay'),
        related_name='recipes',
        verbose_name='автор'
    )
    image = models.ImageField(
        upload_to='images/recipes',
        default=None,
        )
    text = models.TextField(null=False, blank=False)
    cooking_time = models.IntegerField()

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.FloatField()
