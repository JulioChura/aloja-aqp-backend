from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsStudentOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


#  Datos de referencia 
class AccommodationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccommodationStatus.objects.all()
    serializer_class = AccommodationStatusSerializer


class AccommodationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccommodationType.objects.all()
    serializer_class = AccommodationTypeSerializer


class PredefinedServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredefinedService.objects.all()
    serializer_class = PredefinedServiceSerializer


#  Alojamiento 
class PublicAccommodationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccommodationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # Filtra solo los alojamientos con estado "published"
        return Accommodation.objects.filter(status__name__iexact="published").select_related('owner', 'accommodation_type')
    
class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            # Propietario ve solo sus alojamientos
            return Accommodation.objects.filter(owner=user.owner_profile)
        return Accommodation.objects.all()  # Estudiantes ven todos

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'owner_profile'):
            raise PermissionDenied("Solo propietarios pueden crear alojamientos")
        serializer.save(owner=user.owner_profile)


#  Fotos 
class AccommodationPhotoViewSet(viewsets.ModelViewSet):
    queryset = AccommodationPhoto.objects.all()
    serializer_class = AccommodationPhotoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return AccommodationPhoto.objects.filter(accommodation__owner=user.owner_profile)
        return AccommodationPhoto.objects.none()  # Estudiantes no pueden ver aquí, usar nested serializer en alojamiento


#  Servicios 
class AccommodationServiceViewSet(viewsets.ModelViewSet):
    queryset = AccommodationService.objects.all()
    serializer_class = AccommodationServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return AccommodationService.objects.filter(accommodation__owner=user.owner_profile)
        return AccommodationService.objects.none()


#  Distancias a universidades 
class UniversityDistanceViewSet(viewsets.ModelViewSet):
    queryset = UniversityDistance.objects.all()
    serializer_class = UniversityDistanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return UniversityDistance.objects.filter(accommodation__owner=user.owner_profile)
        return UniversityDistance.objects.none()



#  Lugares cercanos 
class AccommodationNearbyPlaceViewSet(viewsets.ModelViewSet):
    queryset = AccommodationNearbyPlace.objects.all()
    serializer_class = AccommodationNearbyPlaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return AccommodationNearbyPlace.objects.filter(accommodation__owner=user.owner_profile)
        return AccommodationNearbyPlace.objects.none()


#  Reseñas 
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return Review.objects.all()
        return Review.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Solo estudiantes pueden dejar reseñas")
        serializer.save(student=user.student_profile)


#  Favoritos 
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return Favorite.objects.filter(student=user.student_profile)
        return Favorite.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Solo estudiantes pueden agregar favoritos")
        serializer.save(student=user.student_profile)


""" 
creando accomodation por partes 
"""

from rest_framework import viewsets, permissions
from .models import Accommodation
from .serializers import AccommodationBasicCreateSerializer, AccommodationSerializer
from .permissions import IsOwnerOrReadOnly

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        # Usar serializer básico solo para crear
        if self.action == 'create':
            return AccommodationBasicCreateSerializer
        return AccommodationSerializer

    def perform_create(self, serializer):
        # Estado inicial "en proceso"
        status_obj = AccommodationStatus.objects.get(name="draft")
        serializer.save(owner=self.request.user.owner_profile, status=status_obj)
        

class AccommodationPhotoBulkCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AccommodationPhotoBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Fotos guardadas correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccommodationServiceBulkCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        serializer = AccommodationServiceBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Servicios guardados correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

