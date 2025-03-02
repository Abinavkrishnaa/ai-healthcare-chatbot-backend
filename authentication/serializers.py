from rest_framework import serializers 
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta  :
        model = CustomUser
        fields=  {
            'username',
            'email',
            'password',
            'age',
            'gender',
            'medical_history',
            'medications'
        }
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            age=validated_data['age'],
            gender=validated_data['gender'],
            medical_history=validated_data['medical_history'],
            medications=validated_data['medications']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user