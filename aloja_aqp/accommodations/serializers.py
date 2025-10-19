# accommodations/serializers.py
from rest_framework import serializers
from .models import (
    AccommodationStatus, AccommodationType, Accommodation, AccommodationPhoto,
    PredefinedService, AccommodationService, UniversityDistance, AccommodationNearbyPlace,
    Review, Favorite
)
from users.models import OwnerProfile, StudentProfile
from universities.models import University, UniversityCampus
from points.models import PointOfInterest

#  SERIALIZERS DE DATOS DE REFERENCIA 
class AccommodationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationStatus
        fields = '__all__'

class AccommodationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationType
        fields = '__all__'

class PredefinedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredefinedService
        fields = '__all__'

#  NESTED SERIALIZERS 
class AccommodationPhotoNestedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = AccommodationPhoto
        fields = ['id', 'image', 'order_num', 'is_main']
    def get_image(self, obj):
        print("evaluando image url nested")
        if obj.image:
            return obj.image.url  # Cloudinary ya devuelve la URL completa
        return None

class AccommodationServiceNestedSerializer(serializers.ModelSerializer):
    service = PredefinedServiceSerializer(read_only=True)

    class Meta:
        model = AccommodationService
        fields = ['id', 'service', 'detail']

class UniversityDistanceNestedSerializer(serializers.ModelSerializer):
    campus = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UniversityDistance
        fields = ['id', 'campus', 'distance_km', 'walk_time_minutes', 'bus_time_minutes']
        
class AccommodationNearbyPlaceNestedSerializer(serializers.ModelSerializer):
    point_of_interest = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AccommodationNearbyPlace
        fields = ['id', 'point_of_interest', 'distance_km', 'walking_time_min']

class ReviewNestedSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.user.email', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'student', 'rating', 'comment', 'review_date', 'status']

class FavoriteNestedSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.user.email', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'student', 'date_added']

#  SERIALIZER PRINCIPAL 
class AccommodationSerializer(serializers.ModelSerializer):
    photos = AccommodationPhotoNestedSerializer(many=True, read_only=True)
    services = AccommodationServiceNestedSerializer(many=True, read_only=True)
    university_distances = UniversityDistanceNestedSerializer(many=True, read_only=True)
    nearby_places = AccommodationNearbyPlaceNestedSerializer(many=True, read_only=True)
    reviews = ReviewNestedSerializer(many=True, read_only=True)
    favorites = FavoriteNestedSerializer(many=True, read_only=True)
    status = serializers.CharField(source="status.name", read_only=True)
    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['owner', 'publication_date', 'created_at', 'updated_at']

#  OTROS SERIALIZERS SIMPLES 
class PhotoSerializer(serializers.Serializer):
    image = serializers.CharField()
    order_num = serializers.IntegerField()
    is_main = serializers.BooleanField()

class AccommodationPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationPhoto
        fields = ['id', 'accommodation', 'image', 'order_num', 'is_main', 'created_at']
        read_only_fields = ['created_at']

class AccommodationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationService
        fields = '__all__'

class UniversityDistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDistance
        fields = '__all__'


class AccommodationNearbyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationNearbyPlace
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['student', 'review_date']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['student', 'date_added']


"""
accommodations/serializers.py
"""
from rest_framework import serializers
from .models import Accommodation

class AccommodationBasicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = [
            'id','title', 'description', 'accommodation_type', 'address',
            'latitude', 'longitude', 'monthly_price', 'coexistence_rules'
        ]

class AccommodationPhotoBulkSerializer(serializers.Serializer):
    accommodation = serializers.IntegerField()
    photos = PhotoSerializer(many=True)

    def create(self, validated_data):
        accommodation_id = validated_data['accommodation']
        try:
            accommodation = Accommodation.objects.get(pk=accommodation_id)
        except Accommodation.DoesNotExist:
            raise serializers.ValidationError("El alojamiento no existe.")
        photos_data = validated_data['photos']
        created_photos = []
        for photo_data in photos_data:
            photo_obj = AccommodationPhoto.objects.create(
                accommodation=accommodation,
                image=photo_data['image'],
                order_num=photo_data.get('order_num', 1),
                is_main=photo_data.get('is_main', False)
            )
            created_photos.append(photo_obj)
        return created_photos

class ServiceBulkSerializer(serializers.Serializer):
    service = serializers.IntegerField()
    detail = serializers.CharField(required=False)

class AccommodationServiceBulkSerializer(serializers.Serializer):
    accommodation = serializers.IntegerField()
    services = ServiceBulkSerializer(many=True)

    def create(self, validated_data):
        accommodation_id = validated_data['accommodation']
        try:
            accommodation = Accommodation.objects.get(pk=accommodation_id)
        except Accommodation.DoesNotExist:
            raise serializers.ValidationError("El alojamiento no existe.")
        services_data = validated_data['services']
        created_services = []
        for service_data in services_data:
            try:
                predefined_service = PredefinedService.objects.get(pk=service_data['service'])
            except PredefinedService.DoesNotExist:
                raise serializers.ValidationError(f"El servicio con id {service_data['service']} no existe.")
            exists = AccommodationService.objects.filter(
                accommodation=accommodation,
                service=predefined_service
            ).exists()
            if not exists:
                service_obj = AccommodationService.objects.create(
                    accommodation=accommodation,
                    service=predefined_service,
                    detail=service_data.get('detail', '')
                )
                created_services.append(service_obj)
        return created_services

class DistanceBulkSerializer(serializers.Serializer):
    campus = serializers.IntegerField()
    distance_km = serializers.DecimalField(max_digits=6, decimal_places=2)
    walk_time_minutes = serializers.IntegerField(required=False)
    bus_time_minutes = serializers.IntegerField(required=False)

class UniversityDistanceBulkSerializer(serializers.Serializer):
    accommodation = serializers.IntegerField()
    distances = DistanceBulkSerializer(many=True)

    def create(self, validated_data):
        accommodation_id = validated_data['accommodation']
        try:
            accommodation = Accommodation.objects.get(pk=accommodation_id)
        except Accommodation.DoesNotExist:
            raise serializers.ValidationError("El alojamiento no existe.")
        distances_data = validated_data['distances']
        created_distances = []
        for dist_data in distances_data:
            try:
                campus = UniversityCampus.objects.get(pk=dist_data['campus'])
            except UniversityCampus.DoesNotExist:
                raise serializers.ValidationError(f"El campus con id {dist_data['campus']} no existe.")
            exists = UniversityDistance.objects.filter(
                accommodation=accommodation,
                campus=campus
            ).exists()
            if not exists:
                dist_obj = UniversityDistance.objects.create(
                    accommodation=accommodation,
                    campus=campus,
                    distance_km=dist_data['distance_km'],
                    walk_time_minutes=dist_data.get('walk_time_minutes'),
                    bus_time_minutes=dist_data.get('bus_time_minutes')
                )
                created_distances.append(dist_obj)
        return created_distances

class NearbyPlaceBulkSerializer(serializers.Serializer):
    point_of_interest = serializers.IntegerField()
    distance_km = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    walking_time_min = serializers.IntegerField(required=False)

class AccommodationNearbyPlaceBulkSerializer(serializers.Serializer):
    accommodation = serializers.IntegerField()
    places = NearbyPlaceBulkSerializer(many=True)

    def create(self, validated_data):
        accommodation_id = validated_data['accommodation']
        try:
            accommodation = Accommodation.objects.get(pk=accommodation_id)
        except Accommodation.DoesNotExist:
            raise serializers.ValidationError("El alojamiento no existe.")
        places_data = validated_data['places']
        created_places = []
        for place_data in places_data:
            try:
                poi = PointOfInterest.objects.get(pk=place_data['point_of_interest'])
            except PointOfInterest.DoesNotExist:
                raise serializers.ValidationError(f"El punto de interés con id {place_data['point_of_interest']} no existe.")
            exists = AccommodationNearbyPlace.objects.filter(
                accommodation=accommodation,
                point_of_interest=poi
            ).exists()
            if not exists:
                place_obj = AccommodationNearbyPlace.objects.create(
                    accommodation=accommodation,
                    point_of_interest=poi,
                    distance_km=place_data.get('distance_km'),
                    walking_time_min=place_data.get('walking_time_min')
                )
                created_places.append(place_obj)
        return created_places

