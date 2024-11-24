from pydantic import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.permissions import IsAdmin
from core.services.deployment import DeploymentService
from core.types.request import NewDeploymentRequestEntity
from core.utils.mixin import BaseResponseMixin


class DeploymentAPIView(APIView, BaseResponseMixin):
    """
    Handles CRUD Of Deployment.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request) -> Response:
        """
        Create `Deployment` State
        """

        try:
            payload = NewDeploymentRequestEntity(**request.data)
        except ValidationError as exception:
            return self.error_response(errors=exception, message="Invalid Payload")

        service = DeploymentService()
        new_deployment = service.create(payload=payload)

        return self.success_response(
            data={"id": new_deployment.id}, message="Deployment created successfully"
        )
