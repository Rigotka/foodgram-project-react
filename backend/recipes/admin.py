from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag, TagsRecipe)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


class TabularInlineIngredient(admin.TabularInline):
    model = IngredientInRecipe


class TabularInlineTag(admin.TabularInline):
    model = TagsRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author',)
    inlines = [TabularInlineIngredient, TabularInlineTag]


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
