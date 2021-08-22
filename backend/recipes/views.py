from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Recipe, Ingredient, Favorite, ShoppingCart
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import TagSerializer, ShowRecipeSerializer, IngredientSerializer, CreateRecipeSerializer, FavoriteSerializer, ShoppingCartSerializer
from rest_framework.decorators import api_view
from .filters import RecipeFilter
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db.models import Sum





class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class FavoriteViewSet(APIView):

    def get(self, request, recipe_id):
        user = request.user
        data = {
            "user": user.id,
            "recipe": recipe_id,
        }
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            return Response(
                {"Ошибка": "Уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavoriteSerializer(
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ShoppingCartViewSet(APIView):

    def get(self, request, recipe_id):
        user = request.user
        data = {
            "user": user.id,
            "recipe": recipe_id,
        }
        shopping_cart_exist = ShoppingCart.objects.filter(
            user=user,
            recipe__id=recipe_id
        ).exists()
        if shopping_cart_exist:
            return Response(
                {"Ошибка": "Уже есть в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        context = {'request': request}
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):

    recipes = Recipe.objects.filter(recipe_shopping_cart__user=request.user)
    ingredients = recipes.values(
        'ingredients__name', 'ingredients__measurement_unit'
    ).annotate(
        total_amount=Sum('recipe_ingredients__amount')
    )
    file_data = ""

    for item in ingredients:
        line = ' '.join(str(value) for value in item.values())
        file_data += line + '\n'

    response = HttpResponse(file_data, 'Content-Type: text/plain') 
    response['Content-Disposition'] = 'attachment; filename="wishlist.txt"' 
    return response
    # for record in shopping_cart:
    #     recipe = record.recipe
    #     ingredients = Ingredient.objects.filter(recipe=recipe)
    #     for ingredient in ingredients:
    #         amount = ingredient.amount
    #         name = ingredient.ingredient.name
    #         measurement_unit = ingredient.ingredient.measurement_unit
    #         if name not in buying_list:
    #             buying_list[name] = {
    #                 'measurement_unit': measurement_unit,
    #                 'amount': amount
    #             }
    #         else:
    #             buying_list[name]['amount'] = (buying_list[name]['amount']
    #                                            + amount)
    # wishlist = []
    # for name, data in buying_list.items():
    #     wishlist.append(
    #         f"{name} - {data['amount']} ({data['measurement_unit']} \n")
    # response = HttpResponse(wishlist, content_type='text/plain')
    # response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
