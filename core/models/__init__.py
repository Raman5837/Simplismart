from typing import Union

from core.models.abstract import AbstractModel
from core.models.deployment import Deployment
from core.models.organization import InviteCode, Membership, Organization
from core.models.resource import Cluster, ResourceAllocation

Models = Union[
    Cluster,
    Membership,
    InviteCode,
    Deployment,
    Organization,
    AbstractModel,
    ResourceAllocation,
]
