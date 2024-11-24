from django.db import transaction
from django.db.models import QuerySet

from core.errors import ResourceDoesNotExistsError
from core.models.organization import Organization
from core.models.resource import Cluster
from core.types.request import ClusterRequestEntity


class ClusterService:
    """
    Service Layer For Clusters
    """

    @transaction.atomic
    def create(self, payload: ClusterRequestEntity) -> Cluster:
        """
        Creates new cluster
        """

        try:
            organization = Organization.objects.get(id=payload.organization_id)
        except Organization.DoesNotExist as exception:
            raise ResourceDoesNotExistsError("Organization does not exists") from exception

        return Cluster.objects.create(
            cpu=payload.cpu,
            gpu=payload.gpu,
            ram=payload.ram,
            name=payload.name,
            organization=organization,
        )

    def list(self) -> QuerySet[Cluster]:
        """
        Returns all `Cluster`
        """

        return Cluster.objects.all()

    def get(self, cluster_id: str) -> Cluster:
        """
        Returns `Cluster` if exists
        """

        try:
            return Cluster.objects.get(id=cluster_id)
        except Exception as exception:
            raise ResourceDoesNotExistsError("Cluster does not exists") from exception
