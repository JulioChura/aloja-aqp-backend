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

class AccommodationSerializer(serializers.ModelSerializer):
    photos = serializers.StringRelatedField(many=True, read_only=True)
    services = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['owner', 'publication_date', 'created_at', 'updated_at']

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
