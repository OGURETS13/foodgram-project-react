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
            # 'password',
            'first_name',
            'last_name',
            'is_subscribed',
            # 'following',
            # 'followers'
        )
        # extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
        # read_only_fields = ('following', 'followers')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            try:
                if obj in user.following.all():
                    return True
                return False
            except (AttributeError):
                return False
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


class CustomUserCreateSerializer(CustomUserSerializer):
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


class SubscribeSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            # 'is_subscribed',
            # 'recipes',
        )


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
    measurment_unit = serializers.SerializerMethodField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurment_unit'
        )
        read_only_fields = ('name',)

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurment_unit(self, obj):
        return obj.ingredient.measurment_unit


class ListRetrieveRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(many=False, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(many=True, read_only=True)

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
        read_only_fields = ('author',)
        extra_kwargs = {"ingredients": {"required": False, "allow_null": True}}

    def get_current_user(self):
        request = self.context.get('request')
        if request:
            return request.user
        return None

    def get_is_favorited(self, obj):
        user = self.get_current_user()
        if obj in user.favorites.all():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_current_user()
        if obj in user.shopping_cart.all():
            return True
        return False

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время готовки должно быть не меньше 1"
            )
        return value


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
        ingredients = validated_data.pop('ingredients')
        tags_pk = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # raise Exception(ingredients)
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient.get('amount'))
            IngredientRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=recipe,
                amount=ingredient['amount']
            )
        for tag_pk in tags_pk:
            tag = get_object_or_404(Tag, pk=tag_pk)
            Recipe.tags.add(tag)
        return recipe

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
