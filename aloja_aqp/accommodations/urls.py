# accommodations/urls.py
from rest_framework import routers
from django.urls import path, include
from .views import *

router = routers.DefaultRouter()
router.register(r'accommodation-status', AccommodationStatusViewSet)
router.register(r'accommodation-types', AccommodationTypeViewSet)
router.register(r'predefined-services', PredefinedServiceViewSet)
router.register(r'accommodations', AccommodationViewSet)
router.register(r'accommodation-photos', AccommodationPhotoViewSet)
router.register(r'accommodation-services', AccommodationServiceViewSet)
router.register(r'university-distances', UniversityDistanceViewSet)
router.register(r'accommodation-nearby-places', AccommodationNearbyPlaceViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'public/accommodations', PublicAccommodationViewSet, basename='public-accommodations')

urlpatterns = [
    path('api/', include(router.urls)),
]
