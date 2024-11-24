from typing import Union

from core.services.cluster import ClusterService
from core.services.deployment import DeploymentService
from core.services.organization import OrganizationService
from core.services.resource import ResourceAllocationService

Services = Union[
    ClusterService, DeploymentService, OrganizationService, ResourceAllocationService
]
