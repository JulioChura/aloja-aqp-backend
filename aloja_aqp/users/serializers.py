from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import OwnerProfile, User, StudentProfile, UserStatus  
from universities.serializers import StudentUniversitySerializer
from universities.models import StudentUniversity
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        attrs['user'] = user
        return attrs
    
class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    universities = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name','universities', 'phone_number']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está en uso.")
        return value

    def create(self, validated_data):
        universities_data = validated_data.pop('universities', [])
        phone_number = validated_data.pop('phone_number', '')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Asignar rol de estudiante
        student_group, _ = Group.objects.get_or_create(name='student')
        user.groups.add(student_group)

        active_status, _ = UserStatus.objects.get_or_create(name='active')

        student_profile = StudentProfile.objects.create(
            user=user,
            phone_number=phone_number,
            status=active_status
        )

        for university_id in universities_data:
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

    owner_group, _ = Group.objects.get_or_create(name='owner')
    user.groups.add(owner_group)

    # Estado por defecto: Activo
    active_status, _ = UserStatus.objects.get_or_create(name='Activo')

    owner_profile = OwnerProfile.objects.create(
        user=user,
        company_name=company_name,
        phone_number=phone_number,
        status=active_status
    )

    return user


class OwnerRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    dni = serializers.CharField(required=True)
    contact_address = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context['request'].user  # usuario logueado

        # evitar crear owner si ya existe
        if hasattr(user, 'owner_profile'):
            raise serializers.ValidationError("El usuario ya tiene perfil de owner.")

        # asignar rol owner
        owner_group, _ = Group.objects.get_or_create(name='owner')
        user.groups.add(owner_group)

        active_status, _ = UserStatus.objects.get_or_create(name='active')

        # crear perfil owner
        owner_profile = OwnerProfile.objects.create(
            user=user,
            phone_number=validated_data.get('phone_number', ''),
            dni=validated_data['dni'],
            contact_address=validated_data.get('contact_address', ''),
            status=active_status
        )

        return owner_profile
    
    

"""
    Respuestas 
"""
from rest_framework import serializers
from .models import User, StudentProfile, OwnerProfile

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['phone_number', 'status_id']

class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = ['phone_number', 'dni', 'contact_address', 'verified', 'status_id']

class UserResponseSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    student_profile = StudentProfileSerializer(read_only=True)
    owner_profile = OwnerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'roles', 'student_profile', 'owner_profile', 'avatar']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_roles(self, obj):
        return [group.name for group in obj.groups.all()]
