import django_filters as filters

from .models import Ingredient, Recipe


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
    is_favorited = filters.BooleanFilter(method='favorite_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='shop_filter')

    def favorite_filter(self, queryset, name, value):
        qs = queryset.filter(is_favorited=value)
        return qs

    def shop_filter(self, queryset, name, value):
        qs = queryset.filter(is_in_shopping_cart=value)
        return qs

    class Meta:
        model = Recipe
        fields = {
            "author": ["exact"],
        }
