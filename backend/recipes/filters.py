import django_filters as filters

from .models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        conjoined=False
    )
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')