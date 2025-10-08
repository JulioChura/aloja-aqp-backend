from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import LoginSerializer, StudentRegistrationSerializer, UserResponseSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import UserResponseSerializer

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