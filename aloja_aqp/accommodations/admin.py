from django.contrib import admin
from .models import (
    Accommodation, AccommodationType, AccommodationStatus, AccommodationPhoto, 
    PredefinedService, AccommodationService, UniversityDistance, 
    AccommodationNearbyPlace, Review, Favorite
)

@admin.register(AccommodationType)
class AccommodationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(AccommodationStatus)
class AccommodationStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class AccommodationPhotoInline(admin.TabularInline):
    model = AccommodationPhoto
    extra = 1

class AccommodationServiceInline(admin.TabularInline):
    model = AccommodationService
    extra = 1

class UniversityDistanceInline(admin.TabularInline):
    model = UniversityDistance
    extra = 1

class NearbyPlaceInline(admin.TabularInline):
    model = AccommodationNearbyPlace
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0

class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    readonly_fields = ('student', 'accommodation', 'date_added')
    can_delete = False

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'accommodation_type', 'status', 'monthly_price', 'publication_date')
    list_filter = ('accommodation_type', 'status', 'publication_date')
    search_fields = ('title', 'owner__user__email', 'address')
    ordering = ('-publication_date',)
    inlines = [AccommodationPhotoInline, AccommodationServiceInline, UniversityDistanceInline, NearbyPlaceInline, ReviewInline, FavoriteInline]

@admin.register(PredefinedService)
class PredefinedServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AccommodationService)
class AccommodationServiceAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'service', 'detail')
    search_fields = ('accommodation__title', 'service__name')
    list_filter = ('service',)

@admin.register(UniversityDistance)
class UniversityDistanceAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'university', 'distance_km', 'walk_time_minutes', 'bus_time_minutes')
    search_fields = ('accommodation__title', 'university__name')

@admin.register(AccommodationNearbyPlace)
class AccommodationNearbyPlaceAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'point_of_interest', 'distance_km', 'walking_time_min')
    search_fields = ('accommodation__title', 'point_of_interest__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'student', 'rating', 'status', 'review_date')
    list_filter = ('status', 'review_date')
    search_fields = ('accommodation__title', 'student__user__email', 'comment')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('student', 'accommodation', 'date_added')
    search_fields = ('student__user__email', 'accommodation__title')
    readonly_fields = ('student', 'accommodation', 'date_added')
