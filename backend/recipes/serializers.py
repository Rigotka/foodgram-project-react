from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag, TagsRecipe)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        qs = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(qs, many=True).data


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

class RecordRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='id'
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'name', 'tags',
                  'cooking_time', 'text', 'image', 'author',)

    def validate_ingredients(self, value):
        ids = [ingredient['id'] for ingredient in value]
        if Ingredient.objects.filter(id__in=ids).count() < len(value):
            raise serializers.ValidationError('Такого ингридиента не существует')
        return value

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Введите целое число больше 0 для времени готовки'
            )
        return data
    @transaction.atomic
    def create(self, validated_data):
        return self.performer(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        return self.performer(validated_data, instance)

    def performer(self, validated_data, recipe=None):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if recipe is None:
            recipe = self.Meta.model.objects.create(**validated_data)
        else:
            IngredientInRecipe.objects.filter(recipe=recipe).delete()
            old_tags = Tag.objects.filter(recipes=recipe)
            for tag in old_tags:
                recipe.tags.remove(tag)
            for key, value in validated_data.items():
                setattr(recipe, key, value)
            recipe.save()
        for tag in tags:
            recipe.tags.add(tag['id'])
            IngredientInRecipe.objects.bulk_create(
                [
                    IngredientInRecipe(
                        recipe=recipe,
                        ingredient=get_object_or_404(
                            Ingredient,
                            id=ingredient['id'],
                        ),
                        amount=ingredient['amount'],
                    ) for ingredient in ingredients
                ]
            )
            return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeSerializer(
            instance.recipe,
            context={'request': request}).data


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
