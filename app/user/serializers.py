"""
Serializers for the user API View
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validate_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validate_data)


    def update(self, instance, validated_data):
        """Update and return user. it is overwriting the update method on the user
        serializer,
        validated_data: the data that already passes through the serialize validation"""
        password = validated_data.pop('password', None)

        # pop the password from validated_data so it can be removed after
        #  separate the udpate password with update other fields
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        #  return the user to the view if required to be used later 
        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    # validate method is called at the validation stage by the view
    # when the data is posted to the view, it's passed to the serializer
    #  to validate if the data is correct
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        # authenticate if the user credention is correct, if correct return user
        #  otherwise return empty object null
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # if raise the error with serializer, the view will translate
            #  it to http 400 bad request and display the message here
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs