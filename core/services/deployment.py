from datetime import datetime
from logging import getLogger
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet

from core.base.redis import RedisClient
from core.constants import DeploymentStatus
from core.errors import BadRequestError, ResourceDoesNotExistsError
from core.models.deployment import Deployment
from core.models.resource import Cluster
from core.services.resource import ResourceAllocationService
from core.types.request import (
    NewDeploymentRequestEntity,
    ResourceAllocationRequestEntity,
)

logger = getLogger(__name__)


class DeploymentService:
    """
    Service Layer For Deployment
    """

    def __init__(self) -> None:
        self.__redis_client = RedisClient()

    def has_sufficient_resources(
        self,
        cpu_required: int,
        gpu_required: int,
        ram_required: int,
        available: Dict[str, int],
    ) -> bool:
        """
        Helper method to check if the available resources are enough for the deployment.
        """

        return (
            available["cpu"] >= cpu_required
            and available["gpu"] >= gpu_required
            and available["ram"] >= ram_required
        )

    @transaction.atomic
    def create(self, payload: NewDeploymentRequestEntity) -> Deployment:
        """
        Creates new `Deployment` state
        """

        try:
            cluster = Cluster.objects.get(id=payload.cluster_id, is_deleted=False)
        except Cluster.DoesNotExist as exception:
            raise ResourceDoesNotExistsError("Cluster does not exists") from exception

        available_resource: Dict[str, int] = cluster.available_resources()
        has_sufficient_resources = self.has_sufficient_resources(
            available=available_resource,
            cpu_required=payload.cpu_required,
            gpu_required=payload.gpu_required,
            ram_required=payload.ram_required,
        )

        if has_sufficient_resources:
            started_at = datetime.now()
            status = DeploymentStatus.IN_PROGRESS
        else:
            started_at = None
            status = DeploymentStatus.QUEUED

        new_deployment = Deployment.objects.create(
            status=status,
            cluster=cluster,
            started_at=started_at,
            priority=payload.priority,
            image_path=payload.image_path,
            cpu_required=payload.cpu_required,
            gpu_required=payload.gpu_required,
            ram_required=payload.ram_required,
        )

        # Let's Allocate resources to the deployment if we've sufficient resource
        if has_sufficient_resources:
            ResourceAllocationService().create(
                payload=ResourceAllocationRequestEntity(
                    cluster_id=cluster.id,
                    deployment_id=new_deployment.id,
                    cpu_allocated=new_deployment.cpu_required,
                    gpu_allocated=new_deployment.gpu_required,
                    ram_allocated=new_deployment.ram_required,
                )
            )
        else:
            # Add deployment to Redis queue if resources are insufficient
            # NOTE:- -ve value, since higher priority deployments should be scheduled first.
            self.__redis_client.z_add(
                "DEPLOYMENT_QUEUE", {new_deployment.id: -new_deployment.priority}
            )

        return new_deployment

    def list(self) -> QuerySet[Deployment]:
        """
        Returns all `Deployment`
        """

        return Deployment.objects.all()

    def get(self, deployment_id: str) -> Deployment:
        """
        Returns `Deployment` if exists
        """

        try:
            return Deployment.objects.select_related("cluster").get(id=deployment_id)
        except Exception as exception:
            raise ResourceDoesNotExistsError("Deployment does not exists") from exception

    @transaction.atomic
    def clean_up_deployment(self, deployment_id: str, status: DeploymentStatus) -> Deployment:
        """
        Marks a deployment as complete and frees resources.
        """

        try:
            deployment = Deployment.objects.get(id=deployment_id, completed_at__isnull=True)
        except Deployment.DoesNotExist as exception:
            raise ResourceDoesNotExistsError("Deployment does not exist") from exception

        if status not in [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED]:
            raise BadRequestError(f"Invalid status '{status}' for finalizing {deployment}")

        # Free the allocated resources
        ResourceAllocationService().release_resources(deployment_id=deployment.id)

        deployment.status = status
        deployment.completed_at = datetime.now()

        deployment.save()
        logger.info(f"[DeploymentService]: {deployment} is completed")

        return deployment
