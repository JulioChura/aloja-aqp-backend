from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsStudentOrReadOnly

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
class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'ownerprofile'):
            # Propietario ve solo sus alojamientos
            return Accommodation.objects.filter(owner=user.ownerprofile)
        return Accommodation.objects.all()  # Estudiantes ven todos

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'ownerprofile'):
            raise PermissionDenied("Solo propietarios pueden crear alojamientos")
        serializer.save(owner=user.ownerprofile)

# Fotos 
class AccommodationPhotoViewSet(viewsets.ModelViewSet):
    queryset = AccommodationPhoto.objects.all()
    serializer_class = AccommodationPhotoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'ownerprofile'):
            return AccommodationPhoto.objects.filter(accommodation__owner=user.ownerprofile)
        return AccommodationPhoto.objects.none()  # Estudiantes no pueden ver aquí, usar nested serializer en alojamiento

#  Servicios 
class AccommodationServiceViewSet(viewsets.ModelViewSet):
    queryset = AccommodationService.objects.all()
    serializer_class = AccommodationServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'ownerprofile'):
            return AccommodationService.objects.filter(accommodation__owner=user.ownerprofile)
        return AccommodationService.objects.none()

#  Distancias a universidades 
class UniversityDistanceViewSet(viewsets.ModelViewSet):
    queryset = UniversityDistance.objects.all()
    serializer_class = UniversityDistanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'ownerprofile'):
            return UniversityDistance.objects.filter(accommodation__owner=user.ownerprofile)
        return UniversityDistance.objects.none()

#  Lugares cercanos 
class AccommodationNearbyPlaceViewSet(viewsets.ModelViewSet):
    queryset = AccommodationNearbyPlace.objects.all()
    serializer_class = AccommodationNearbyPlaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'ownerprofile'):
            return AccommodationNearbyPlace.objects.filter(accommodation__owner=user.ownerprofile)
        return AccommodationNearbyPlace.objects.none()

# Reseñas 
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'studentprofile'):
            return Review.objects.all()
        return Review.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'studentprofile'):
            raise PermissionDenied("Solo estudiantes pueden dejar reseñas")
        serializer.save(student=user.studentprofile)

#  Favoritos 
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'studentprofile'):
            return Favorite.objects.filter(student=user.studentprofile)
        return Favorite.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'studentprofile'):
            raise PermissionDenied("Solo estudiantes pueden agregar favoritos")
        serializer.save(student=user.studentprofile)
