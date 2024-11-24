from typing import Dict

from django.db import models

from core.models.abstract import AbstractModel
from core.models.organization import Organization


class Cluster(AbstractModel):
    """
    Cluster and its resource pool.
    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    cpu = models.PositiveIntegerField()  # Total CPU cores
    ram = models.PositiveIntegerField()  # Total RAM in MB
    gpu = models.PositiveIntegerField()  # Total GPU units

    def available_resources(self) -> Dict[str, int]:
        """
        Returns the available resources in the cluster.
        """

        allocated = self.resource_allocations.aggregate(
            cpu_allocated=models.Sum("cpu_allocated"),
            ram_allocated=models.Sum("ram_allocated"),
            gpu_allocated=models.Sum("gpu_allocated"),
        )

        return {
            "cpu": self.cpu - (allocated["cpu_allocated"] or 0),
            "ram": self.ram - (allocated["ram_allocated"] or 0),
            "gpu": self.gpu - (allocated["gpu_allocated"] or 0),
        }

    def __str__(self) -> str:
        return f"<Cluster> {self.name} {self.organization}"


class ResourceAllocation(AbstractModel):
    """
    Stores allocation details for a resource in a cluster.
    """

    cluster = models.ForeignKey(
        Cluster, on_delete=models.CASCADE, related_name="resource_allocations"
    )
    deployment = models.OneToOneField(
        "Deployment", on_delete=models.CASCADE, related_name="resource_allocation"
    )

    cpu_allocated = models.PositiveIntegerField()
    ram_allocated = models.PositiveIntegerField()
    gpu_allocated = models.PositiveIntegerField()
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"<ResourceAllocation> {self.id}"
