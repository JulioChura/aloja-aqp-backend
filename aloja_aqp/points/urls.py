from rest_framework import routers
from .views import PointTypeViewSet, PointOfInterestViewSet

router = routers.DefaultRouter()
router.register(r'point-types', PointTypeViewSet)
router.register(r'points-of-interest', PointOfInterestViewSet)

urlpatterns = router.urls