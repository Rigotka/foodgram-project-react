from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, Value
from django.db.models.query import Prefetch

from users.models import User


# class RecipeQueryset(models.QuerySet):
#     def annotate_user_flags(self, user):
#         if user.is_anonymous:
#             return self.annotate(
#                 is_favorited=Value(
#                     False, output_field=models.BooleanField()
#                 ),
#                 is_in_shopping_cart=Value(
#                     False, output_field=models.BooleanField()
#                 )
#             )
#         return self.annotate(
#             is_favorited=Exists(Favorite.objects.filter(
#                 user=user, recipe_id=OuterRef('pk')
#             )),
#             is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
#                 userr=user, recipe_id=OuterRef('pk')
#             ))
#         )
class RecipeQueryset(models.QuerySet):
    def with_favorites(self, user=None):
        subquery = Favorite.objects.filter(
            user=user,
            recipe=OuterRef("id"),
        )
        qs = self.annotate(is_favorited=Exists(subquery))
        return qs

    def with_shopping_cart(self, user=None):
        subquery = ShoppingCart.objects.filter(
            user=user,
            recipe=OuterRef("id"),
        )
        qs = self.annotate(is_in_shopping_cart=Exists(subquery))
        return qs


class Tag(models.Model):
    name = models.CharField(max_length=200, blank=False,
                            null=True, unique=True)
    color = models.CharField(max_length=200, blank=False,
                             null=True, unique=True)
    slug = models.SlugField(max_length=200, blank=False,
                            null=True, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False,
                            null=True, unique=True)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe'
    )
    tags = models.ManyToManyField(Tag, through='TagsRecipe')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Время приготовления должно быть больше 0')]
    )
    objects = RecipeQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pk', )


class TagsRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Количество ингредиента должно быть больше 0')]
    )

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'favorit'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_shopping_cart"
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'shoplist'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping')
        ]

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
