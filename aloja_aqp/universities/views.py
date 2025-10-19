from rest_framework import viewsets
from .models import UniversityCampus
from .serializers import UniversityCampusSimpleSerializer

# Create your views here.
class UniversityCampusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UniversityCampus.objects.all()
    serializer_class = UniversityCampusSimpleSerializer