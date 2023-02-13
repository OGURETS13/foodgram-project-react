from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='iexact'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping'
    )

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            filtered_queryset = queryset.filter(pk__in=user.favorites.all())
        if value == 0:
            filtered_queryset = queryset.exclude(pk__in=user.favorites.all())
        return filtered_queryset

    def filter_shopping(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            filtered_queryset = queryset.filter(
                pk__in=user.shopping_cart.all()
            )
        if value == 0:
            filtered_queryset = queryset.exclude(
                pk__in=user.shopping_cart.all()
            )
        return filtered_queryset

    class Meta:
        model = Recipe
        fields = ['tags__slug', 'author']
