from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Usuario registrado exitosamente",
            "user_id": user.id,  
            "email": user.email 
        }, status=status.HTTP_201_CREATED)