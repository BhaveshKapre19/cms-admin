from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrOwner(BasePermission):
    """
    Admin can access any object.
    User can access only their own object.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to anyone (if you want)
        if request.method in SAFE_METHODS:
            return True

        # Admin / superuser can do anything
        if request.user and request.user.is_staff:
            return True

        # User can modify ONLY their own profile
        return obj == request.user

class IsUserActive(BasePermission):
    """
    Allows access only to active users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active
    
class IsVerifiedUser(BasePermission):
    """
    Allows access only to verified users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_verified