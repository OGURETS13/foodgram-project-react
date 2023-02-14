import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return user.following.filter(pk=obj.pk).exists()
        return False

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AnonymousUserSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
        )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )
        read_only_fields = ('name',)

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class AnonymousRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)
    author = AnonymousUserSerializer(many=False, required=False)
    ingredients = IngredientRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class ListRetrieveRecipeSerializer(AnonymousRecipeSerializer):
    author = CustomUserSerializer(many=False, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_current_user(self):
        request = self.context.get('request')
        if request:
            return request.user
        return None

    def get_is_favorited(self, obj):
        user = self.get_current_user()
        return user.favorites.filter(pk=obj.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_current_user()
        return user.shopping_cart.filter(pk=obj.pk).exists()


class RecipeCreateUpdateSerializer(ListRetrieveRecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_null=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
    )

    def create(self, validated_data):
        non_val_ingredients = self.context['request'].data['ingredients']
        validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in non_val_ingredients:
            ingredient_obj = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            ingredient_recipe = [
                IngredientRecipe(
                    ingredient=ingredient_obj,
                    recipe=recipe,
                    amount=ingredient['amount']
                )
            ]
        IngredientRecipe.objects.bulk_create(
                ingredient_recipe,
                ignore_conflicts=True
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        if self.context['request'].data.get('ingredients') is not None:
            non_val_ingredients = self.context['request'].data['ingredients']
            validated_data.pop('ingredients')
            recipe.ingredients.all().delete()
            for ingredient in non_val_ingredients:
                ingredient_obj = get_object_or_404(
                    Ingredient,
                    pk=ingredient.get('id')
                )
                ingredient_recipe = [
                    IngredientRecipe(
                        ingredient=ingredient_obj,
                        recipe=recipe,
                        amount=ingredient['amount']
                    )
                ]
            IngredientRecipe.objects.bulk_create(
                    ingredient_recipe,
                    ignore_conflicts=True
                )
        if self.context['request'].data.get('tags') is not None:
            tags = validated_data.pop('tags')
            old_tags = recipe.tags.all()
            for old_tag in old_tags:
                recipe.tags.remove(old_tag)
            for tag in tags:
                recipe.tags.add(tag)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = ListRetrieveRecipeSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)
        extra_kwargs = {"ingredients": {"required": False, "allow_null": True}}


class SimpleRecipeSerializer(ListRetrieveRecipeSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'name',
            'cooking_time'
        )


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit is None:
            recipes_limit = 5
        else:
            recipes_limit = int(recipes_limit)
        recipes = obj.recipes.all()[:recipes_limit]
        return SimpleRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes_number = obj.recipes.all().count()
        return recipes_number
