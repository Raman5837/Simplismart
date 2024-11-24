from typing import Union

from pydantic import BaseModel, Field, PositiveInt, constr

from core.constants import UserRole


class ClusterRequestEntity(BaseModel):
    """
    Request entity for `Cluster`
    """

    cpu: PositiveInt
    ram: PositiveInt
    gpu: PositiveInt
    name: constr(max_length=255)
    organization_id: Union[str, int]


class OrganizationRequestEntity(BaseModel):
    """
    Request entity to create an `Organization`
    """

    name: constr(max_length=255)


class MembershipRequestEntity(BaseModel):
    """
    Request entity to join an `Organization`
    """

    role: UserRole
    invite_code: str

    class Config:
        from_attributes = True


class NewDeploymentRequestEntity(BaseModel):
    """
    Request entity to create `Deployment`
    """

    priority: PositiveInt
    cpu_required: PositiveInt
    ram_required: PositiveInt
    gpu_required: PositiveInt

    cluster_id: Union[str, int]
    image_path: str = Field(..., max_length=512, description="Docker image path")


class ResourceAllocationRequestEntity(BaseModel):
    """
    Request entity to create `ResourceAllocation`
    """

    cluster_id: Union[str, int]
    deployment_id: Union[str, int]

    cpu_allocated: PositiveInt
    ram_allocated: PositiveInt
    gpu_allocated: PositiveInt
