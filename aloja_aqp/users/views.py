from django.contrib.auth.models import Group
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import LoginSerializer, StudentRegistrationSerializer, UserResponseSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, OwnerProfile, UserStatus
from .serializers import UserResponseSerializer, OwnerRegistrationSerializer,  UserUpdateSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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


