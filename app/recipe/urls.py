"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

# DefaultRouter used as a API view to automatically create router
# for all the options in the view
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()

# create a new endpoint named /recipes and assign all the different
# endpoints from the recipe view set to that endpoint, can do all CURD
#  through this endpoint
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'


# get the url registered by router, finally need to wire up with the main
#  url in app/urls
urlpatterns = [
    path('', include(router.urls))
]