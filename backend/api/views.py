from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets  # generics, status
# from rest_framework.decorators import action
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny  # IsAuthenticatedOrReadOnly

from recipes.models import Recipe
from users.models import User
from .serializers import (
    CustomUserSerializer,
    RecipeCreateUpdateSerializer,
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


class RecipeViewset(viewsets.ModelViewSet):
    model = Recipe
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
