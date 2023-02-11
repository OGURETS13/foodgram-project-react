from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag
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
        # 'favourites'
    )


admin.site.register(User, UserAdmin)

admin.site.register(Tag)

admin.site.register(Recipe)

admin.site.register(Ingredient)
