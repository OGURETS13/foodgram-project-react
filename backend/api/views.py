import io

from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from fpdf import FPDF
from rest_framework import filters, generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from recipes.models import Ingredient, Recipe, Tag
from users.models import User
from api.filters import RecipeFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
    AnonymousRecipeSerializer,
    AnonymousUserSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    ListRetrieveRecipeSerializer,
    RecipeCreateUpdateSerializer,
    SubscriptionsSerializer,
    TagSerializer
)


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    model = User
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        user = self.request.user
        if user.is_anonymous:
            return AnonymousUserSerializer
        return self.serializer_class


class APISubscribe(APIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target = get_object_or_404(User, pk=pk)
        user = self.request.user
        user.following.add(target)
        serializer = CustomUserSerializer(target, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target = get_object_or_404(User, pk=pk)
        user = self.request.user
        user.following.remove(target)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIFavorite(APIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        user.favorites.add(recipe)
        serializer = RecipeCreateUpdateSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIToShoppingCart(APIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        user.shopping_cart.add(recipe)
        serializer = RecipeCreateUpdateSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetShoppingCart(APIView):
    def get(self, request):
        user = request.user
        recipes = user.shopping_cart.all()
        ingredients = {}
        for recipe in recipes:
            ingredient_recipe_queryset = recipe.ingredients.all()
            for ingredient_recipe in ingredient_recipe_queryset:
                ingredient = ingredient_recipe.ingredient
                id = ingredient.id
                name = ingredient.name
                unit = ingredient.measurement_unit
                amount = ingredient_recipe.amount

                if id in ingredients:
                    ingredients[id][1] += amount
                else:
                    ingredients[id] = [name, amount, unit]

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            family='Attractive',
            style='',
            fname=r'/app/font/Attractive-Regular.ttf'
        )
        pdf.set_font('Attractive', "", 16)
        for ingredient in ingredients.values():
            ingredient_line = (
                ingredient[0].capitalize()
                + ' - '
                + str(ingredient[1])
                + ' '
                + ingredient[2]
            )
            pdf.cell(
                40,
                10,
                ingredient_line,
                new_x="LMARGIN",
                new_y="NEXT",
                align='L'
            )
        buffer = io.BytesIO(bytes(pdf.output()))
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


class SubscriptionList(generics.ListAPIView):
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.following.all()
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    serializer_class = RecipeCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        user = self.request.user
        if (self.action == 'list') or (self.action == 'retrieve'):
            if user.is_anonymous:
                return AnonymousRecipeSerializer
            return ListRetrieveRecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
