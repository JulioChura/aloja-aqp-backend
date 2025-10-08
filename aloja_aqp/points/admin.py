from django.contrib import admin
from .models import PointType, PointOfInterest

@admin.register(PointType)
class PointTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'address', 'latitude', 'longitude')
    list_filter = ('type',)
    search_fields = ('name', 'address', 'type__name')
