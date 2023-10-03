"""
Tests for models
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
#  need to import this when testing model other than user model
from core import models

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user, create a test user we can use to assign to our tag"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test models"""
        email = 'test1@example.com'
        password = 'testpass1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['Test3@EXAMPLE.COM', 'Test3@example.com'],
            ['Test4@example.COM', 'Test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_creat_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        '''Test creating a tag is successful
        This test to thing one is we have correct string representation set up for model instances
        2 is we can create a tag instance '''
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # unit test for the function created for creating the path to the file in the system
    # decorator to patch the UUID function imported into model,
    # it generally generates a string of  unique identifier (mock the behaviour)
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        #  function that generated the path to the image that is being uploaded
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
