from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAuthorOrReadOnly
from .paginator import PageLimitSetPagination
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend 
from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecordRecipeSerializer, ShoppingCartSerializer,
                          ShowRecipeSerializer, TagSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_class = IngredientFilter
    search_fields = ['name', ]
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return RecordRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteAndShoppingCartViewSet(APIView):
    permission_classes = [IsAuthorOrReadOnly]
    main_obj = Recipe

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'author': user.id,
            'recipes': recipe_id
        }
        serializer = self.serializer_class(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        deletion_obj = get_object_or_404(
            self.second_obj, author=user, recipes_id=recipe_id
        )
        deletion_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(FavoriteAndShoppingCartViewSet):
    second_obj = Favorite
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(FavoriteAndShoppingCartViewSet):
    second_obj = ShoppingCart
    serializer_class = ShoppingCartSerializer


@api_view(['GET'])
def download_shopping_cart(request):

    recipes = Recipe.objects.filter(recipe_shopping_cart__user=request.user)
    ingredients = recipes.values(
        'ingredients__name', 'ingredients__measurement_unit'
    ).annotate(
        total_amount=Sum('recipe_ingredients__amount')
    )
    file_data = []

    for item in ingredients:
        file_data.append('\n'.join(str(value) for value in item.values()))

    response = HttpResponse(file_data, 'Content-Type: text/plain')
    response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
    return response
