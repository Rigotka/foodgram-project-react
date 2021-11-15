from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj.id).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        request = self.context.get('request')
        author_id = data['author'].id
        follow_exists = Subscription.objects.filter(
            user=request.user,
            author__id=author_id
        ).exists()
        if request.method == 'GET':
            if request.user.id == author_id:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя'
                )
            if follow_exists:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя'
                )
        return data


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ListSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj.author
            )[:int(limit)]

        return SubscriptionRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


# class GetRecipesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')


# class ShowSubscriptionSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
#     recipes = serializers.SerializerMethodField('get_recipes')
#     recipes_count = serializers.SerializerMethodField('get_recipes_count')

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name',
#             'is_subscribed', 'recipes', 'recipes_count'
#         )
#         #read_only_fields = fields

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if request is None or request.user.is_anonymous:
#             return False
#         user = request.user
#         return Subscription.objects.filter(author=obj, user=user).exists()

#     def get_recipes(self, obj):
#         recipes = Recipe.objects.filter(author=obj)
#         return GetRecipesSerializer(recipes, many=True).data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()


# class SubscriptionSerializer(serializers.ModelSerializer):
#     queryset = User.objects.all()
#     user = serializers.PrimaryKeyRelatedField(queryset=queryset)
#     author = serializers.PrimaryKeyRelatedField(queryset=queryset)

#     class Meta:
#         model = Subscription
#         fields = ('user', 'author')

#     def validate(self, data):
#         user = self.context.get('request').user
#         author_id = data['author'].id
#         follow_exist = Subscription.objects.filter(
#             user=user,
#             author__id=author_id
#         ).exists()

#         if self.context.get('request').method == 'GET':
#             if user.id == author_id or follow_exist:
#                 raise serializers.ValidationError(
#                     'Нельзя подписываться дважды')
#         return data

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return ShowSubscriptionSerializer(
#             instance.author,
#             context=context).data
#