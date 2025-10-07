from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, StudentProfile  

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    university = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'university']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está en uso.")
        return value
    
    def create(self, validated_data):
        university = validated_data.pop('university', '')
        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data.get('first_name', ''),
            last_name = validated_data.get('last_name', ''),
            is_student = True
        )
        StudentProfile.objects.create(user=user, university=university)
        
        return user