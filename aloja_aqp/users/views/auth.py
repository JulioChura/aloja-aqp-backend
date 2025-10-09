from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..models import User
from ..serializers import (
    LoginSerializer,
    StudentRegistrationSerializer,
    OwnerRegistrationSerializer,
    ChangePasswordSerializer,
    UserResponseSerializer
)
from ..utils.tokens import generate_tokens_for_user


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer  

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_data = UserResponseSerializer(user).data
        tokens = generate_tokens_for_user(user)
        return Response({"user": user_data, **tokens}, status=status.HTTP_200_OK)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StudentRegistrationSerializer

    def create(self, request):
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

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        owner_profile = serializer.save()
        user_data = UserResponseSerializer(owner_profile.user).data
        return Response({
            "message": "Perfil de propietario creado exitosamente",
            "user": user_data
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            token = RefreshToken(request.data["refresh"])
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
