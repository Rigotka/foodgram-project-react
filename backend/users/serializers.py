from django.contrib.auth import models
from rest_framework import fields, serializers
from rest_framework.status import is_success
from .models import User, Subscription
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self,obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(author=obj, user=user).exists()


class GetRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    recipes = serializers.SerializerMethodField('get_recipe')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name','is_subscribed','recipes','recipes_count')
        
    def create(self, author):
        user = self.context.get('request').user
        return Subscription.objects.create(user=user, following=author)

    def get_is_subscribed(self,obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(author=obj, user=user).exists()

    def get_recipe(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return GetRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj).count()
        return count




# class ShowSubscriptionSerializer(serializers.ModelSerializer):
#     recipes = serializers.SerializerMethodField('get_recipe')
#     recipes_count = serializers.SerializerMethodField('get_recipes_count')
#     is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

#     def get_recipe(self, obj):
#         author = obj.following
#         recipes = Recipe.objects.filter(author=author)
#         return GetRecipesSerializer(recipes, many=True).data
    
#     def get_recipes_count(self, obj):
#         author = obj.following
#         count = Recipe.objects.filter(author=author).count()
#         return count

#     def get_is_subscribed(self,obj):
#         request = self.context.get('request')
#         if request is None or request.user.is_anonymous:
#             return False
#         user = request.user
#         return Subscription.objects.filter(author=obj, user=user).exists()