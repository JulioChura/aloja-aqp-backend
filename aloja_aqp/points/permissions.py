from rest_framework import permissions

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite solo lectura a usuarios normales, escritura solo a admin/staff o owner.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or hasattr(request.user, 'owner_profile'))