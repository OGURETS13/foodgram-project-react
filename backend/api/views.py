from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, viewsets, status
# from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag
from users.models import User
from api.filters import RecipeFilter
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    NewSerializerABetterOne,
    TagSerializer
)


class CustomUserViewSet(UserViewSet):
    model = User
    serializer_class = CustomUserSerializer


class APISubscribe(APIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target = get_object_or_404(User, pk=pk)
        user = self.request.user
        user.following.add(target)
        serializer = CustomUserSerializer(target)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIFavourite(APIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        user.favourites.add(recipe)
        serializer = RecipeCreateUpdateSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIToShoppingCart(APIView):
    def post(self, request, **kwargs):
        pk = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        user.shopping_cart.add(recipe)
        serializer = RecipeCreateUpdateSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionList(generics.ListAPIView):
    serializer_class = CustomUserSerializer

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


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def get_serializer(self, *args, **kwargs):
        if (self.action == 'list') or (self.action == 'retrieve'):
            return NewSerializerABetterOne(*args, **kwargs)
        return self.serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
