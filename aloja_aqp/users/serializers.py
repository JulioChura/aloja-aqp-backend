from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import OwnerProfile, User, StudentProfile, UserStatus  
from universities.serializers import StudentUniversitySerializer
from universities.models import StudentUniversity
from users.models import Role

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    universities = StudentUniversitySerializer(many=True, write_only=True) 
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name','universities', 'phone_number']
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
        universities_data = validated_data.pop('universities', [])
        phone_number = validated_data.pop('phone_number', '')

        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data.get('first_name', ''),
            last_name = validated_data.get('last_name', ''),
        )
        
        student_role, _ = Role.objects.get_or_create(name='student')
        user.roles.add(student_role)
        
        active_status, _ = UserStatus.objects.get_or_create(name='Activo')

        student_profile = StudentProfile.objects.create(
            user=user,
            phone_number=phone_number,
            status=active_status
        )      
        
        for uni_data in universities_data:
            university_id = uni_data['id']  
            StudentUniversity.objects.create(
                student=student_profile,
                university_id=university_id
            )
        return user


# falta probar
from users.models import UserStatus

def create(self, validated_data):
    phone_number = validated_data.pop('phone_number', '')
    company_name = validated_data.pop('company_name', '')

    user = User.objects.create_user(
        email=validated_data['email'],
        password=validated_data['password'],
        first_name=validated_data.get('first_name', ''),
        last_name=validated_data.get('last_name', ''),
    )

    # Rol por defecto: owner
    from users.models import Role
    owner_role, _ = Role.objects.get_or_create(name='owner')
    user.roles.add(owner_role)

    # Estado por defecto: Activo
    active_status, _ = UserStatus.objects.get_or_create(name='Activo')

    owner_profile = OwnerProfile.objects.create(
        user=user,
        company_name=company_name,
        phone_number=phone_number,
        status=active_status
    )

    return user
