# views/owner.py
from rest_framework import generics
from ..models import OwnerProfile
from ..serializers import OwnerProfileSViewDataSerializer

class OwnerProfileDetailView(generics.RetrieveAPIView):
    queryset = OwnerProfile.objects.all()
    serializer_class = OwnerProfileSViewDataSerializer
    lookup_field = 'id'  # permite usar /owners/<id>/
