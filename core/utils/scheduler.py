from datetime import datetime
from logging import getLogger

from core.base.redis import RedisClient
from core.constants import DeploymentStatus
from core.errors import ResourceDoesNotExistsError
from core.models.deployment import Deployment
from core.services.deployment import DeploymentService
from core.services.resource import ResourceAllocationService
from core.types.request import ResourceAllocationRequestEntity

logger = getLogger(__name__)


class Scheduler:
    """
    Queued Deployment Scheduler Class
    """

    def __init__(self) -> None:
        self.__redis_client = RedisClient()
        self.__REDIS_KEY: str = "DEPLOYMENT_QUEUE"

        self.__deployment_service = DeploymentService()
        self.__allocation_service = ResourceAllocationService()

    def schedule_deployment(self) -> None:
        """
        Schedules deployments from the Redis queue to clusters based on priority and resource availability.
        """

        # All highest-priority deployment from Redis
        deployment_ids = self.__redis_client.z_range_by_score(self.__REDIS_KEY, "-inf", "+inf")

        if not deployment_ids:
            logger.info("[Scheduler]: No deployments in the queue...")
            return

        logger.info(f"[Scheduler]: {len(deployment_ids)} deployments to schedule...")

        for deployment_id in deployment_ids:
            try:
                deployment = self.__deployment_service.get(deployment_id=deployment_id)

                if deployment.status != DeploymentStatus.QUEUED:
                    logger.warning(f"[Scheduler]: {deployment} is already in terminal state")
                    self.__redis_client.z_rem(self.__REDIS_KEY, deployment_id)
                    continue

                # If the cluster associated with the deployment is deleted
                if deployment.cluster.is_deleted:
                    logger.warning(f"[Scheduler]: {deployment.cluster} is deleted.")
                    self.__redis_client.z_rem(self.__REDIS_KEY, deployment_id)
                    continue

                available_resources = deployment.cluster.available_resources()

                if self.__deployment_service.has_sufficient_resources(
                    available=available_resources,
                    cpu_required=deployment.cpu_required,
                    gpu_required=deployment.gpu_required,
                    ram_required=deployment.ram_required,
                ):
                    self.__allocate_resource(deployment)
                else:
                    logger.info(f"[Scheduler]: {deployment} cannot be scheduled due to insufficient resources.")

            except ResourceDoesNotExistsError:
                self.__redis_client.z_rem(self.__REDIS_KEY, deployment_id)
                logger.exception(f"[Scheduler]: Deployment {deployment_id} does not exist.")
                continue

            except Exception as exception:
                logger.exception(f"[Scheduler]: Got un-handled exception {exception}")
                continue

    def __allocate_resource(self, deployment: Deployment) -> None:
        """ """

        self.__allocation_service.create(
            payload=ResourceAllocationRequestEntity(
                deployment_id=deployment.id,
                cluster_id=deployment.cluster_id,
                cpu_allocated=deployment.cpu_required,
                gpu_allocated=deployment.gpu_required,
                ram_allocated=deployment.ram_required,
            )
        )

        # Update deployment status to progress
        deployment.started_at = datetime.now()
        deployment.status = DeploymentStatus.IN_PROGRESS
        deployment.save()

        # Remove deployment from Redis queue
        self.__redis_client.z_rem(self.__REDIS_KEY, deployment.id)
        logger.info(f"[Scheduler]: {deployment} scheduled successfully on cluster {deployment.cluster}")

    def cleanup_completed_deployments(self) -> None:
        """
        Frees resources for deployments that are marked as completed or failed.
        """

        logger.info("[Scheduler]: Checking for completed/failed deployments to cleanup...")

        all_deployments = self.__deployment_service.list()

        terminals = all_deployments.filter(
            is_deleted=False,
            status__in=[DeploymentStatus.COMPLETED, DeploymentStatus.FAILED],
        )

        for deployment in terminals:
            try:
                self.__deployment_service.clean_up_deployment(deployment_id=deployment.id, status=deployment.status)
                logger.info(f"[Scheduler]: {deployment} is marked as {deployment.status} and resources are cleaned up.")
            except Exception as exception:
                logger.exception(f"[Scheduler]: Failed to cleanup deployment {deployment}, Err: {exception}")
                continue
