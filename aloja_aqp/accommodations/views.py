from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsStudentOrReadOnly,IsAccommodationOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Count, Q
from decimal import Decimal
from django.db.models import Min
from rest_framework.pagination import PageNumberPagination


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
    # Paginate only this viewset: 10 items per page
    class TenPerPagePagination(PageNumberPagination):
        page_size = 6
    pagination_class = TenPerPagePagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # Filtra solo los alojamientos con estado "published"
        return Accommodation.objects.filter(status__name__iexact="published").select_related('owner', 'accommodation_type')

    @action(detail=False, methods=['get'], url_path='autocomplete')
    def autocomplete(self, request):
        q = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 8))
        if not q:
            return Response([], status=200)
        qs = self.get_queryset().filter(Q(title__icontains=q) | Q(address__icontains=q))[:limit]
        results = []
        for a in qs:
            thumb = None
            first_photo = a.photos.first()
            if first_photo and first_photo.image:
                thumb = first_photo.image.url
            results.append({
                'id': a.id,
                'title': a.title,
                'address': a.address,
                'monthly_price': str(a.monthly_price),
                'rooms': a.rooms,
                'thumbnail': thumb,
            })
        return Response(results)

    @action(detail=False, methods=['get'], url_path='filter')
    def filter_accommodations(self, request):
        qs = self.get_queryset()
        # full-text like filters
        q = request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(address__icontains=q))

        # university / campus filters (via UniversityDistance)
        campus_id = request.GET.get('campus_id')
        university_id = request.GET.get('university_id')
        if campus_id:
            # Use the actual reverse relation name present on Accommodation model
            # (no explicit related_name was set on UniversityDistance.accommodation)
            # available lookups include 'universitydistance' (see FieldError choices)
            qs = qs.filter(universitydistance__campus__id=campus_id)
        elif university_id:
            # filter accommodations that have a distance entry to any campus of the university
            qs = qs.filter(universitydistance__campus__university__id=university_id)

        # price range
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        try:
            if min_price is not None and min_price != '':
                qs = qs.filter(monthly_price__gte=Decimal(min_price))
            if max_price is not None and max_price != '':
                qs = qs.filter(monthly_price__lte=Decimal(max_price))
        except Exception:
            pass

        # rooms
        min_rooms = request.GET.get('min_rooms')
        max_rooms = request.GET.get('max_rooms')
        if min_rooms:
            try:
                qs = qs.filter(rooms__gte=int(min_rooms))
            except Exception:
                pass
        if max_rooms:
            try:
                qs = qs.filter(rooms__lte=int(max_rooms))
            except Exception:
                pass

        # services: expect comma separated ids, require accommodations that include ALL selected services
        services = request.GET.get('services')
        if services:
            try:
                service_ids = [int(s) for s in services.split(',') if s]
                if service_ids:
                    # filter accommodations that have services in the list
                    qs = qs.filter(services__service__id__in=service_ids).annotate(
                        matched_services=Count('services__service', filter=Q(services__service__id__in=service_ids), distinct=True)
                    ).filter(matched_services__gte=len(service_ids))
            except Exception:
                pass

        qs = qs.distinct()
        # Ordering: if a university is selected, order by the minimum distance to that university's campuses
        if university_id:
            try:
                qs = qs.annotate(
                    min_distance=Min('universitydistance__distance_km', filter=Q(universitydistance__campus__university__id=university_id))
                ).order_by('min_distance', 'monthly_price')
            except Exception:
                # fallback to default ordering
                qs = qs.order_by('monthly_price')
        else:
            # default ordering: by monthly price ascending
            qs = qs.order_by('monthly_price')
        page = self.paginate_queryset(qs)
        serializer_context = {'request': request}
        if university_id:
            serializer_context['selected_university_id'] = university_id

        if page is not None:
            serializer = self.get_serializer(page, many=True, context=serializer_context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True, context=serializer_context)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='debug/campus-info')
    def debug_campus_info(self, request):
        """Temporary diagnostic endpoint.

        Usage: /api/public/accommodations/debug/campus-info/?campus_id=1
        Returns: universitydistance entries for the campus and related accommodations (with status and key fields)
        """
        campus_id = request.GET.get('campus_id')
        if not campus_id:
            return Response({'error': 'campus_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cd = UniversityDistance.objects.filter(campus__id=campus_id).select_related('campus', 'accommodation')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        distances = []
        ac_ids = []
        for d in cd:
            distances.append({
                'id': d.id,
                'accommodation_id': d.accommodation.id if d.accommodation_id else None,
                'campus_id': d.campus.id if d.campus_id else None,
                'distance_km': str(d.distance_km),
                'walk_time_minutes': d.walk_time_minutes,
                'bus_time_minutes': d.bus_time_minutes,
            })
            if d.accommodation_id:
                ac_ids.append(d.accommodation_id)

        accommodations = []
        if ac_ids:
            qs = Accommodation.objects.filter(id__in=ac_ids).select_related('status')
            for a in qs:
                accommodations.append({
                    'id': a.id,
                    'title': a.title,
                    'monthly_price': str(a.monthly_price),
                    'rooms': a.rooms,
                    'status': a.status.name if a.status else None,
                    'latitude': a.latitude,
                    'longitude': a.longitude,
                })

        # include campus coords too
        campus_info = None
        try:
            campus_obj = None
            from universities.models import UniversityCampus
            campus_obj = UniversityCampus.objects.filter(id=campus_id).first()
            if campus_obj:
                campus_info = {
                    'id': campus_obj.id,
                    'name': str(campus_obj),
                    'latitude': getattr(campus_obj, 'latitude', None),
                    'longitude': getattr(campus_obj, 'longitude', None),
                }
        except Exception:
            campus_info = None

        return Response({
            'campus': campus_info,
            'distances': distances,
            'accommodations': accommodations,
        })
 

class AccommodationPhotoViewSet(viewsets.ModelViewSet):
    queryset = AccommodationPhoto.objects.all()
    serializer_class = AccommodationPhotoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAccommodationOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return AccommodationPhoto.objects.filter(accommodation__owner=user.owner_profile)
        return AccommodationPhoto.objects.none()  # Estudiantes no pueden ver aquí, usar nested serializer en alojamiento


#  Servicios 
class AccommodationServiceViewSet(viewsets.ModelViewSet):
    queryset = AccommodationService.objects.all()
    serializer_class = AccommodationServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAccommodationOwnerOrReadOnly]

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



class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return AccommodationBasicCreateSerializer
        return AccommodationSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'owner_profile'):
            return Accommodation.objects.filter(owner=user.owner_profile).exclude(status__name="deleted")
        return Accommodation.objects.all().exclude(status__name="deleted")

    def perform_create(self, serializer):
        status_obj = AccommodationStatus.objects.get(name="draft")
        serializer.save(owner=self.request.user.owner_profile, status=status_obj)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def publish(self, request, pk=None):
        accommodation = self.get_object()
        status_obj = AccommodationStatus.objects.get(name="published")
        accommodation.status = status_obj
        accommodation.save()
        return Response({"detail": "Alojamiento publicado correctamente."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def hide(self, request, pk=None):
        accommodation = self.get_object()
        status_obj = AccommodationStatus.objects.get(name="hidden")
        accommodation.status = status_obj
        accommodation.save()
        return Response({"detail": "Alojamiento ocultado correctamente."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly], url_path="delete-original")
    def delete_logical(self, request, pk=None):
        accommodation = self.get_object()
        status_obj = AccommodationStatus.objects.get(name="deleted")
        accommodation.status = status_obj
        accommodation.save()
        return Response({"detail": "Alojamiento borrado correctamente."}, status=status.HTTP_200_OK)
   
    
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

class UniversityDistanceBulkCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        serializer = UniversityDistanceBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Distancias guardadas correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccommodationNearbyPlaceBulkCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        serializer = AccommodationNearbyPlaceBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Lugares cercanos guardados correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

