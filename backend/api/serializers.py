import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    # is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'following',
            'followers'
        )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

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


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(many=False, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)
        extra_kwargs = {"ingredients": {"required": False, "allow_null": True}}

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время готовки должно быть не меньше 1"
            )
        return value
