from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from users.serializers import UserSerializer
from django.db.models import F

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)

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
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, recipe):
        qs = IngredientInRecipe.objects.filter(recipe=recipe)
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

    def create_bulk_ingredients(self, recipe, ingredients_data):
        print(ingredients_data)
        # IngredientInRecipe.objects.bulk_create([
        #     IngredientInRecipe(
        #         ingredient=ingredient['ingredient'],
        #         recipe=recipe,
        #         amount=ingredient['amount']
        #     ) for ingredient in ingredients_data
        # ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_bulk_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_bulk_ingredients(instance, ingredients_data)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        data = ShowRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
        return data


    # def validate_ingredients(self, value):
    #     ingredients = self.initial_data.get('ingredients')
    #     if not ingredients:
    #         raise serializers.ValidationError({'ingredients': 'Список ингредиентов пуст'})
    #     ingredients = value['ingredients']
    #     for ingredient in ingredients:
    #         if ingredient['amount'] <= 0:
    #             raise serializers.ValidationError(
    #                 {'ingredients': 'Rоличество ингридиента должно быть больше 0'})
    #     return value

    # def validate_cooking_time(self, value):
    #     cooking_time = self.initial_data.get('cooking_time')
    #     if int(cooking_time) < 1:
    #         raise serializers.ValidationError({'cooking_time': 'Время приготовления должно быть больше 0'})

    # def create_ingredients(self, recipe, ingredients):
    #     for ingredient in ingredients:
    #         ingr_obj = get_object_or_404(
    #             Ingredient,
    #             id=ingredient['ingredient'].id
    #         )
    #         amount = ingredient['amount']
    #         if IngredientInRecipe.objects.filter(
    #                 recipe=recipe,
    #                 ingredient=ingr_obj
    #         ).exists():
    #             amount += F('amount')
    #         IngredientInRecipe.objects.update_or_create(
    #             defaults={'amount': amount},
    #             recipe=recipe,
    #             ingredient=ingr_obj,
    #         )

    # @transaction.atomic
    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     author = self.context.get('request').user
    #     recipe = Recipe.objects.create(author=author, **validated_data)
    #     recipe.tags.set(tags)
    #     self.create_ingredients(recipe, ingredients)
    #     return recipe

    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     if 'tags' in self.initial_data:
    #         tags = validated_data.pop('tags')
    #         instance.tags.set(tags)
    #     if 'ingredients' in self.initial_data:
    #         ingredients = validated_data.pop('ingredients')
    #         instance.ingredients.clear()
    #         self.create_ingredients(instance, ingredients)
    #     instance.name = validated_data.get(
    #         'name',
    #         instance.name
    #     )
    #     instance.text = validated_data.get(
    #         'text',
    #         instance.text
    #     )
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time',
    #         instance.cooking_time
    #     )
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.save()
    #     return instance


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = "__all__"

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeSerializer(
            instance.recipe,
            context={'request': request}).data


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
