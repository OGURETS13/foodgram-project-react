from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        null=False,
        blank=False
    )


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
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
