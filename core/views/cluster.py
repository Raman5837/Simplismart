from pydantic import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.permissions import IsAdmin
from core.serializers.cluster import ClusterSerializer
from core.services.cluster import ClusterService
from core.types.request import ClusterRequestEntity
from core.utils.mixin import BaseResponseMixin


class ClusterAPIView(APIView, BaseResponseMixin):
    """
    Handles CRUD Of clusters.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request: Request) -> Response:
        """
        Return All Cluster Metadata
        """

        _ = request
        service = ClusterService()

        try:
            clusters = service.list()
            serialized = ClusterSerializer(clusters, many=True)
            return self.success_response(
                data=serialized.data, message="Clusters Metadata"
            )
        except Exception as exception:
            return self.error_response(errors=exception, message="Something went wrong")

    def post(self, request: Request) -> Response:
        """
        Create new Cluster
        """

        try:
            payload = ClusterRequestEntity(**request.data)
        except ValidationError as exception:
            return self.error_response(errors=exception, message="Invalid Payload")

        service = ClusterService()
        new_cluster = service.create(payload=payload)

        return self.success_response(
            data={"id": new_cluster.id}, message="Cluster created successfully"
        )
