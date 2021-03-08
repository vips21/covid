import uuid
from .models import User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.authtoken.models import Token


# Serializers define the API representation.
class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'country_code')
        extra_kwargs = {'password': {'write_only':True}}

    def create(self, validated_data):
        email = validated_data.get('email')
        password =  validated_data.get('password')
        if not email:
            raise ValidationError(
                "Please provide email")
        user = User.objects.filter(email=email).first()
        if user and user.is_active:
            raise PermissionDenied(
                "An account with this email already exists.")
        user = User(email=email)
        user.set_password(password)
        user.first_name=validated_data.get('first_name')
        user.last_name=validated_data.get('last_name')
        user.country_code=validated_data.get('country_code')
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label = 'Email')

    class Meta:
        model = User
        fields = ('email', 'password')
                        
    def validate(self, data):
        user_obj = None
        response = {}
        email =  data.get('email', None)
        password =  data.get('password', None)
        # Fetching user with email
        user = User.objects.filter(email=email).first()
        if user:
            # User exists
            user_obj = user
        else:
            # User does not exist
            response['message'] = "This email is not registered."
            raise ValidationError(response)
        
        if user_obj:
            # Checking password is correct or not
            if not user_obj.check_password(password):
                # Incorrect password
                response['message'] = "Password is incorrect."
                raise ValidationError(response)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'country_code')
        read_only_fields = ('id', 'email')