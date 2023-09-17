"""
views for the recipe APIs
"""
from rest_framework import (
    viewsets,
    # mixins is you can mix in to a view to add additional functionality
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
)
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    # in all cases excpet listing, we want to use the detailSerializer
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # make the retrieved recipes filter down to authenticated user level
    def get_queryset(self):
        """override to the get_queryset, retrieve recipe for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # the method gets called when Dj rest fram wants to determine
    # the class being used for a particular, can help dynamically choose the specific serializer
    def get_serializer_class(self):
        """Return the serializer class for request"""
        # it means a request to retrieve a list of objects
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # when we perform a creation of new object(recipe) through this
        # model viewset, we call this method as part of obkect creation
        #  set the user value to the current authenticated user
        # when save the object of recipe
        serializer.save(user=self.request.user)

# add the CRUD implemetation to the tag model
class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """generic view set allow to throw mix in so can have viewset functionality for the particular
    Mnage tags in the db"""
    serializers_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset down to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')