from django.contrib import admin
from .models import University, StudentUniversity

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'address', 'latitude', 'longitude', 'created_at', 'updated_at')
    search_fields = ('name', 'abbreviation', 'address')
    list_filter = ('created_at',)

@admin.register(StudentUniversity)
class StudentUniversityAdmin(admin.ModelAdmin):
    list_display = ('student', 'university')
    search_fields = ('student__user__email', 'university__name', 'university__abbreviation')
    list_filter = ('university',)
