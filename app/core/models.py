"""
Database models
"""

import uuid
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

# function to determine the path where we want to store our image
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


#  AbstractBaseUser class contains the functionality for auth system but not any fields
#  PermissionsMixin class contains the functionality for the permission feature of Django
#  and it also contains any fields that are needed for the permissions feature
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # assign the user manager to the custom user class
    objects = UserManager()

    # here replace the user name default fields that comes with the default user to custom
    #  email field
    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    """Recipt object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    # we could have manay recipes with many tags, any receipe can be associated with any tags vice versa
    tags = models.ManyToManyField('Tag')

    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self) -> str:
        return self.title

class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        #  if the user deleted the tag associated with the user will also be deleted
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredient for recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

