import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag
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
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'following',
            'followers'
        )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
        read_only_fields = ('following', 'followers')

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


class NewSerializerABetterOne(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(many=False, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)
        extra_kwargs = {"ingredients": {"required": False, "allow_null": True}}

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            try:
                if obj in user.favorites.all():
                    return True
                return False
            except (AttributeError):
                return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            try:
                if obj in user.shopping_cart.all():
                    return True
                return False
            except (AttributeError):
                return False

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время готовки должно быть не меньше 1"
            )
        return value


class RecipeCreateUpdateSerializer(NewSerializerABetterOne):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)
        extra_kwargs = {"ingredients": {"required": False, "allow_null": True}}
