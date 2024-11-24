from rest_framework.permissions import BasePermission
from rest_framework.request import Request


from core.constants import UserRole


class IsAdmin(BasePermission):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request: Request, view):
        _ = view
        return request.user.membership.role == UserRole.ADMIN


class IsDeveloper(BasePermission):
    """
    Allows access only to Developers.
    """

    def has_permission(self, request: Request, view):
        _ = view
        return request.user.membership.role in [UserRole.ADMIN, UserRole.DEVELOPER]


class IsViewer(BasePermission):
    """
    Allows access only to Viewers.
    """

    def has_permission(self, request: Request, view):
        _ = view
        return request.user.membership.role in [UserRole.ADMIN, UserRole.VIEWER]
