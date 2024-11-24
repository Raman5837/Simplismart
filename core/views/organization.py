from pydantic import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.permissions import IsAdmin
from core.serializers.organization import OrganizationSerializer
from core.services.organization import OrganizationService
from core.types.request import OrganizationRequestEntity
from core.utils.mixin import BaseResponseMixin


class OrganizationAPIView(APIView, BaseResponseMixin):
    """
    Handles CRUD Of Organization.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request: Request) -> Response:
        """
        Return All Organization Metadata
        """

        _ = request
        service = OrganizationService()

        try:
            organizations = service.list()
            serialized = OrganizationSerializer(organizations, many=True)
            return self.success_response(
                data=serialized.data, message="Organizations Metadata"
            )
        except Exception as exception:
            return self.error_response(errors=exception, message="Something went wrong")

    def post(self, request: Request) -> Response:
        """
        Create new Organization
        """

        try:
            payload = OrganizationRequestEntity(request.data)
        except ValidationError as exception:
            return self.error_response(errors=exception, message="Invalid Payload")

        service = OrganizationService()
        organization = service.create(payload=payload)

        serialized = OrganizationSerializer(organization)
        return self.success_response(
            data=serialized.data, message="Organization created successfully"
        )
