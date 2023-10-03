"""
views for the recipe APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    # mixins is you can mix in to a view to add additional functionality
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers

# decorator used to update documentation for filtering
@extend_schema_view(
    # extend the schema for the list endpoint
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                # name of the paramter passed in order to filter
                'tags',
                # type is string
                OpenApiTypes.STR,
                description='Comma separated list of IDs of filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separarted list of ingredient Ids to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    # in all cases excpet listing, we want to use the detailSerializer
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    # make the retrieved recipes filter down to authenticated user level
    def get_queryset(self):
        """override to the get_queryset, retrieve recipe for authenticated user"""
        # return self.queryset.filter(user=self.request.user).order_by('-id')

        # refactor the code to support the optional filtering for parameter of common separated list
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # syntax for filtering unrelated fields on db, filters the tags by the id
            # tags__id__in=tag_id means filter objects where the 'id' of related tags is in the list of tag_ids
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    # the method gets called when Dj rest fram wants to determine
    # the class being used for a particular, can help dynamically choose the specific serializer
    def get_serializer_class(self):
        """Return the serializer class for request"""
        # it means a request to retrieve a list of objects
        # action aere ways you can addd different functionality
        # on top of viewsets, default action is create
        # default action list includes (list, update, delete)
        if self.action == 'list':
            return serializers.RecipeSerializer

        # add a custom action type 'upload_image'
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # when we perform a creation of new object(recipe) through this
        # model viewset, we call this method as part of obkect creation
        #  set the user value to the current authenticated user
        # when save the object of recipe
        serializer.save(user=self.request.user)

    # only expect a post request, detail = True means action is apply to the detail portion
    #  (specific id of recipe) non-detail means the generic list view of all recipes
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""

        # get the recipe using the primary key
        recipe = self.get_object()

        #  get the image serializer
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():

            # save the image to the db
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                # define a API parameter assigned_Only
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned by recipes.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        # mixins.UpdateModelMixin make the router automatically
                        # adds the detail API endpoint so we can get the detailed
                        #  API endpoint for the item that we're going to manage
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset down to authenticated user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            # if assigned_only is true, then apply an additional filter to the queryset
            #  recipe__isnull=False means there is a recipe associated with the value
#  recipe__isnull=False is a query filter condition that uses the double-underscore notation (__) to navigate related fields. In this case, it checks if there is an associated recipe for the current object.
# When recipe__isnull=False, it means that there is a related recipe for the current object. Conversely, if recipe__isnull=True, there is no related recipe.
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()
        # return self.queryset.filter(user=self.request.user).order_by('-name')

# add the CRUD implemetation to the tag model
class TagViewSet(BaseRecipeAttrViewSet):
    """generic view set allow to throw mix in so can have viewset functionality for the particular
    Mnage tags in the db"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the db"""
    serializer_class = serializers.IngredientSerializer
    # set our queryset to the ingredients objects tell django what models
    # we want to be manageable through ingredientvieset
    queryset = Ingredient.objects.all()
    # add support for using token authentication only option
    # for authentication on viewset
    # authentication_classes = [TokenAuthentication]

    # all the user need to be authenticated to use the viewset
    # permission_classes = [IsAuthenticated]
