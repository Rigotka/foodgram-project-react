from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


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
        validators=[MinValueValidator(1,), ]
    )

    def __str__(self):
        return self.name


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
        null=True,
        verbose_name='Количество ингредиента'
    )

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
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
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping')
        ]

    def __str__(self):
        return f'{self.recipe}'
