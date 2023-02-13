from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class UserAdmin(admin.ModelAdmin):
    fields = (
        'username',
        'password',
        'is_superuser',
        'is_staff',
        'email',
        'first_name',
        'last_name',
        'user_permissions',
        'favorites',
        'following'
    )
    search_fields = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'image',
        'tags',
        'author',
        'cooking_time',
    )

    list_display = ('name', 'author', 'get_favorited_count')
    search_fields = ('name', 'author')
    list_filter = ('tags',)

    def get_favorited_count(self, obj):
        return obj.recipe_fans.all().count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)

admin.site.register(Tag)

admin.site.register(Recipe, RecipeAdmin)

admin.site.register(Ingredient, IngredientAdmin)

admin.site.register(IngredientRecipe)
