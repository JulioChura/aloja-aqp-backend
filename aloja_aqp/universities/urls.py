from rest_framework import routers
from django.urls import path, include
from .views import UniversityCampusViewSet, UniversityViewSet

router = routers.DefaultRouter()
router.register(r'university-campuses', UniversityCampusViewSet, basename='universitycampus')
router.register(r'universities', UniversityViewSet, basename='university')

urlpatterns = [
    path('', include(router.urls)),
]