from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCreatorOrReadOnly(BasePermission):
    """Anyone logged in can view doctors, but only whoever added one can edit/delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by == request.user
