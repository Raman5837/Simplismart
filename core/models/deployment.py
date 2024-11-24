from django.db import models

from core.constants import DeploymentStatus
from core.models.abstract import AbstractModel
from core.models.resource import Cluster


class Deployment(AbstractModel):
    """
    Stores deployment metadata.
    """

    priority = models.IntegerField()  # Higher priority has higher value
    cpu_required = models.PositiveIntegerField()
    ram_required = models.PositiveIntegerField()
    gpu_required = models.PositiveIntegerField()

    image_path = models.CharField(max_length=512)
    cluster = models.ForeignKey(
        Cluster, on_delete=models.CASCADE, related_name="deployments"
    )
    status = models.CharField(
        max_length=32, choices=DeploymentStatus.choices, default=DeploymentStatus.QUEUED
    )

    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "priority", "queued_at"]),
        ]

    def __str__(self) -> str:
        return f"<Deployment> {self.id} - {self.status}"
