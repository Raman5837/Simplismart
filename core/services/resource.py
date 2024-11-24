from logging import getLogger

from django.db import transaction
from django.db.models import QuerySet

from core.errors import ResourceDoesNotExistsError
from core.models.deployment import Deployment
from core.models.resource import Cluster, ResourceAllocation
from core.types.request import ResourceAllocationRequestEntity

logger = getLogger(__name__)


class ResourceAllocationService:
    """
    Service Layer For ResourceAllocation
    """

    @transaction.atomic
    def create(self, payload: ResourceAllocationRequestEntity) -> ResourceAllocation:
        """
        Creates new `ResourceAllocation`
        """

        try:
            cluster = Cluster.objects.get(id=payload.cluster_id)
        except Cluster.DoesNotExist as exception:
            raise ResourceDoesNotExistsError("cluster does not exists") from exception

        try:
            deployment = Deployment.objects.get(id=payload.deployment_id)
        except Deployment.DoesNotExist as exception:
            raise ResourceDoesNotExistsError(
                "Deployment does not exists"
            ) from exception

        return ResourceAllocation.objects.create(
            cluster=cluster,
            deployment=deployment,
            cpu_allocated=payload.cpu_allocated,
            gpu_allocated=payload.gpu_allocated,
            ram_allocated=payload.ram_allocated,
        )

    def list(self) -> QuerySet[ResourceAllocation]:
        """
        Returns all `ResourceAllocation`
        """

        return ResourceAllocation.objects.all()

    def get(self, allocation_id: str) -> ResourceAllocation:
        """
        Returns `ResourceAllocation` if exists
        """

        try:
            return ResourceAllocation.objects.get(id=allocation_id)
        except Exception as exception:
            raise ResourceDoesNotExistsError(
                "ResourceAllocation does not exists"
            ) from exception

    @transaction.atomic
    def release_resources(self, deployment_id: str) -> None:
        """
        Releases resources allocated to a specific deployment.
        """

        try:
            allocation = ResourceAllocation.objects.get(deployment_id=deployment_id)
            deployment: Deployment = allocation.deployment

            # Update cluster's resources by adding back the allocated resources
            cluster = allocation.cluster
            cluster.cpu += allocation.cpu_allocated
            cluster.gpu += allocation.gpu_allocated
            cluster.ram += allocation.ram_allocated
            cluster.save()

            logger.info(
                f"[ResourceAllocationService]: Released resources for {deployment}"
            )
            allocation.delete()

        except ResourceAllocation.DoesNotExist as exception:
            logger.exception(
                f"[ResourceAllocationService]: Resource allocation for {deployment_id} does not exist."
            )
            raise ResourceDoesNotExistsError(
                "Resource allocation does not exist."
            ) from exception

        except Exception as exception:
            logger.exception(f"[ResourceAllocationService]: {exception}")
            raise
