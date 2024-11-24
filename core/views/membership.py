from pydantic import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.permissions import IsAdmin
from core.services.membership import MembershipService
from core.types.request import MembershipRequestEntity
from core.utils.mixin import BaseResponseMixin


class MembershipAPIView(APIView, BaseResponseMixin):
    """
    Handles CRUD Of Membership.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request) -> Response:
        """
        Join an Organization
        """

        try:
            payload = MembershipRequestEntity(**request.data)
        except ValidationError as exception:
            return self.error_response(errors=exception, message="Invalid Payload")

        service = MembershipService()
        membership = service.create(user=request.user, payload=payload)

        return self.success_response(
            data={"id": membership.id}, message="Membership created successfully"
        )
