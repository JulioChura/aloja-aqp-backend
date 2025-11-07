from rest_framework import viewsets
from .models import University, UniversityCampus
from .serializers import UniversityCampusSimpleSerializer, UniversitySerializer


class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer

# Create your views here.
class UniversityCampusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UniversityCampus.objects.all()
    serializer_class = UniversityCampusSimpleSerializer