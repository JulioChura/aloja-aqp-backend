from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Solo el propietario puede editar o eliminar su alojamiento.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, 'owner') and obj.owner.user == request.user

class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Solo el estudiante dueño de la acción puede modificar sus reseñas o favoritos.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, 'student') and obj.student.user == request.user
