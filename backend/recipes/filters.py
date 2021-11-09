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
    is_favorited = filters.BooleanFilter(method='get_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_favorited(self, query, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(recipe_shopping_cart__user=user)
        return Recipe.objects.all()

    # def favorite_filter(self, queryset, name, value):
    #     qs = queryset.filter(is_favorited=value)
    #     return qs

    # def shop_filter(self, queryset, name, value):
    #     qs = queryset.filter(is_in_shopping_cart=value)
    #     return qs

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
        # fields = {
        #     "author": ["exact"],
        # }
