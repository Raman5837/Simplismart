from pydantic import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.permissions import IsAdmin
from core.services.resource import ResourceAllocationService
from core.types.request import ResourceAllocationRequestEntity
from core.utils.mixin import BaseResponseMixin


class ResourceAllocationAPIView(APIView, BaseResponseMixin):
    """
    Handles CRUD Of `ResourceAllocation`.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request) -> Response:
        """
        Allocate `Resource` To A `Deployment`
        """

        try:
            payload = ResourceAllocationRequestEntity(**request.data)
        except ValidationError as exception:
            return self.error_response(errors=exception, message="Invalid Payload")

        service = ResourceAllocationService()
        allocation = service.create(payload=payload)

        return self.success_response(
            data={"id": allocation.id}, message="Resource allocated successfully"
        )
