"""
Serializer for recipe API
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
)

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view. it is using RecipeSerializer
    as the baseclass since it is an extension to it and inherit all attributes
    from it"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

        