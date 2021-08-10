from apps.core.serializers import UserSerializer
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import check_password

import pytest 

@pytest.mark.django_db
def test_user_serialization(logged_in_user):
    """Ensure User object is created with a hashed password."""
    user_payload = {"username": "keaton" ,"email": "keaton@dotmodus.com", "password": "vERYsTrONGpASSWORD"}
    result =  UserSerializer(data=user_payload)
    assert result.is_valid()
    assert check_password(user_payload['password'], result.validated_data['password'])

@pytest.mark.django_db
def test_user_validation_errors(logged_in_user):
    """Ensure the expected validation errors are raised."""
    result =  UserSerializer(data={"email": "", "password": ""})
    assert result.is_valid() == False
    assert "email" in result.errors 
    assert "password" in result.errors 