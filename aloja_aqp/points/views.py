from rest_framework import viewsets, permissions
from .models import PointType, PointOfInterest
from .serializers import PointTypeSerializer, PointOfInterestSerializer
from .permissions import IsAdminOrOwnerOrReadOnly

class PointTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PointType.objects.all()
    serializer_class = PointTypeSerializer

class PointOfInterestViewSet(viewsets.ModelViewSet):
    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer
    permission_classes = [IsAdminOrOwnerOrReadOnly]