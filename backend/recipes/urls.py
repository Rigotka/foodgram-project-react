from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagsViewSet, RecipesViewSet, IngredientViewSet, FavoriteViewSet, ShoppingCartViewSet, download_shopping_cart

router_v1 = DefaultRouter()

router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipesViewSet, basename='recipes')



urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download'
    ),
    path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view(), name='favorite'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='shopping_cart'
    ),
    path('', include(router_v1.urls)),
]
