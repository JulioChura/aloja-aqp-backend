from rest_framework import routers
from django.urls import path, include
from .views import UniversityCampusViewSet

router = routers.DefaultRouter()
router.register(r'university-campuses', UniversityCampusViewSet, basename='universitycampus')

urlpatterns = [
    path('', include(router.urls)),
]