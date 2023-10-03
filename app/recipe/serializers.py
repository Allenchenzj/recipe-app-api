"""
Serializer for recipe API
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # many=True means it is a list
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)


    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags',
                  'ingredients',]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    # the method should be internal use only, dont expect anyone using this
    # serializer to make calls to this method directly, should only be used
    #  by other methods inside the recipe serializer, reason is for refactoring
    def _get_or_create_ingredients(self, ingredients, recipe):
        """handel getting or creating ingredients as needsss"""
        # it either gets an existing ingredients or create a new ingredients

        # retrieving the authenticated user first
        auth_user = self.context['request'].user
        # loop through all the ingredients
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)


    def create(self, validated_date):
        """Create a recipe"""
        tags = validated_date.pop('tags', [])
        ingredients = validated_date.pop('ingredients', [])
        # separate the recipe main components creation with the tags
        # and ingredients creation
        recipe = Recipe.objects.create(**validated_date)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """update recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        # clear the tags of instance recipe if the tags is empty or not empty list
        # then use get_or_create_tags to add tags iteratively to the recipe
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # add all the rest attribute update to the instance recipe
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view. it is using RecipeSerializer
    as the baseclass since it is an extension to it and inherit all attributes
    from it"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes
    create a separate serializer for uploading the image on the top
    of the original recipe serializer"""

    # it's best practice to only upload one type data to an API
    # want to have a specific separate API just for handling the image
    # upload to make our API data structures

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

