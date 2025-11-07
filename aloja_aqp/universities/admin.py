from django.contrib import admin
from .models import University, StudentUniversity, UniversityCampus
from django.utils.html import format_html

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'address', 'logo_preview', 'created_at', 'updated_at')
    search_fields = ('name', 'abbreviation', 'address')
    list_filter = ('created_at',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:30px;object-fit:contain;"/>', obj.logo)
        return ''
    logo_preview.short_description = 'Logo'


@admin.register(StudentUniversity)
class StudentUniversityAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_university', 'get_campus')
    search_fields = ('student__user__email', 'campus__name', 'campus__university__name', 'campus__university__abbreviation')
    list_filter = ('campus__university',)

    def get_university(self, obj):
        return obj.campus.university.name
    get_university.short_description = 'University'

    def get_campus(self, obj):
        return obj.campus.name
    get_campus.short_description = 'Campus'

@admin.register(UniversityCampus)
class UniversityCampusAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'university', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'university__name', 'address')
    list_filter = ('university',)
