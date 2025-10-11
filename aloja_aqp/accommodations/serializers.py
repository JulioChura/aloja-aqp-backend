# accommodations/serializers.py
from rest_framework import serializers
from .models import (
    AccommodationStatus, AccommodationType, Accommodation, AccommodationPhoto,
    PredefinedService, AccommodationService, UniversityDistance, AccommodationNearbyPlace,
    Review, Favorite
)
from users.models import OwnerProfile, StudentProfile
from universities.models import University
from points.models import PointOfInterest

# ----- SERIALIZERS DE DATOS DE REFERENCIA -----
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

# ----- NESTED SERIALIZERS -----
class AccommodationPhotoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationPhoto
        fields = ['id', 'image', 'order_num', 'is_main']

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

    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['owner', 'publication_date', 'created_at', 'updated_at']

#  OTROS SERIALIZERS SIMPLES 
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
