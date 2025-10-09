from django.contrib.auth.models import Group
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import LoginSerializer, StudentRegistrationSerializer, UserResponseSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, OwnerProfile, UserStatus, StudentProfile
from .serializers import UserResponseSerializer, OwnerRegistrationSerializer,  UserUpdateSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from google.oauth2 import id_token
from google.auth.transport import requests
import os

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginAPIView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({'error': 'ID Token no proporcionado'}, status=400)
        
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture_url = idinfo.get('picture', None)

            user, created = User.objects.get_or_create(email=email)
            
            if created:
                user.first_name = first_name
                user.last_name = last_name
                user.google_id = idinfo['sub']
                user.set_unusable_password()
                if picture_url:
                    user.avatar = picture_url
                user.save()

                student_group, _ = Group.objects.get_or_create(name='student')
                user.groups.add(student_group)

                active_status, _ = UserStatus.objects.get_or_create(name='active')
                StudentProfile.objects.create(
                    user=user,
                    phone_number='',
                    status=active_status
                )

            user_data = UserResponseSerializer(user).data

            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

            return Response({
                "user": user_data,
                **tokens
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': 'Token inválido', 'details': str(e)}, status=400)
        except Exception as e:
            # Captura cualquier otro error y lo imprime en consola
            print("ERROR GoogleLoginAPIView:", e)
            return Response({'error': str(e)}, status=500)


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer  

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user'] 
        user_data = UserResponseSerializer(user).data

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        return Response({
            "user": user_data,
            **tokens
        }, status=status.HTTP_200_OK)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response_serializer = UserResponseSerializer(user)
        
        return Response({
            "message": "Usuario registrado exitosamente",
            "user": response_serializer.data
        }, status=status.HTTP_201_CREATED)
        
class OwnerRegistrationView(generics.CreateAPIView):
    serializer_class = OwnerRegistrationSerializer
    permission_classes = [IsAuthenticated]  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        owner_profile = serializer.save()  

        user = owner_profile.user  
        user_data = UserResponseSerializer(user).data

        return Response({
            "message": "Perfil de propietario creado exitosamente",
            "user": user_data
        }, status=status.HTTP_201_CREATED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Contraseña actualizada correctamente"}, status=status.HTTP_200_OK)
    
# actualizar informacion
class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


