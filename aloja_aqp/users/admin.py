from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Campos que se muestran al EDITAR un usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'avatar_url', 'google_id')}),
        ('Roles y permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),  # Removido 'created_at' y 'updated_at'
    )
    
    # Campos que se muestran al CREAR un usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')}
        ),
    )
    
    # Campos de solo lectura (para mostrar pero no editar)
    readonly_fields = ('date_joined', 'last_login')  # Puedes agregar 'created_at' y 'updated_at' si quieres verlos