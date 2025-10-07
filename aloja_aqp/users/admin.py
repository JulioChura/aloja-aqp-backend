from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'is_student', 'is_owner', 'is_staff', 'is_active', 'date_joined']
    
    list_filter = ['is_student', 'is_owner', 'is_staff', 'is_active', 'date_joined']
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'avatar_url', 'google_id')}),

        ('Roles y permisos', {'fields': ('is_student', 'is_owner', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_student', 'is_owner', 'is_staff', 'is_active')}
        ),
    )
    
    readonly_fields = ('date_joined', 'last_login')