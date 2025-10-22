from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Solo el propietario puede editar o eliminar su alojamiento.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Verifica que el usuario sea el owner del alojamiento
        return hasattr(obj, 'owner') and obj.owner.user == request.user

class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Solo el estudiante dueño de la acción puede modificar sus reseñas o favoritos.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, 'student_profile') and obj.student.user == request.user

class IsAccommodationOwnerOrReadOnly(permissions.BasePermission):
    """
    Solo el dueño del alojamiento asociado puede modificar/eliminar el servicio.
    """
    def has_object_permission(self, request, view, obj):
        # Permitir lectura (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Comprobar propiedad
        user_owner = getattr(request.user, "owner_profile", None)
        accommodation_owner = getattr(obj.accommodation, "owner", None)
        return user_owner == accommodation_owner
    