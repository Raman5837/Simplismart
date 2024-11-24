from typing import Union

from core.views.cluster import ClusterAPIView
from core.views.deployment import DeploymentAPIView
from core.views.membership import MembershipAPIView
from core.views.organization import OrganizationAPIView
from core.views.resource import ResourceAllocationAPIView
from core.views.token import TokenAPIView

Views = Union[
    TokenAPIView,
    ClusterAPIView,
    DeploymentAPIView,
    MembershipAPIView,
    OrganizationAPIView,
    ResourceAllocationAPIView,
]
