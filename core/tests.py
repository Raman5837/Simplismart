from json import dumps
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.constants import DeploymentStatus
from core.models import Cluster, Deployment, Organization
from core.services import DeploymentService, ResourceAllocationService
from core.types.request import (
    NewDeploymentRequestEntity,
    ResourceAllocationRequestEntity,
)


class LoginTestCase(TestCase):
    """
    Test Cases For Login Using JWT
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user_data = {"username": "test_user", "password": "password@123"}
        self.user = User.objects.create_user(**self.user_data)

    def test_login_success(self):
        """
        Test login with valid credentials
        """

        response = self.client.post(
            path=reverse("auth"),
            data=dumps(
                {
                    "username": self.user_data["username"],
                    "password": self.user_data["password"],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("access_token", response.data["data"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials
        """

        response = self.client.post(
            path=reverse("auth"),
            content_type="application/json",
            data=dumps(
                {"username": self.user_data["username"], "password": "wrong_password"}
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user_not_found(self):
        """
        Test login with non-existent user
        """

        response = self.client.post(
            path=reverse("auth"),
            content_type="application/json",
            data=dumps({"username": "non_existent_user", "password": "password@123"}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ResourceAllocationTestCase(TestCase):
    """
    Test Cases For Resource Allocation
    """

    def setUp(self) -> None:
        self.organization = Organization.objects.create(name="Test Organization 1")
        self.cluster = Cluster.objects.create(
            gpu=4,
            cpu=16,
            ram=64 * 1024,
            name="Test Cluster",
            organization=self.organization,
        )

        self.deployment = Deployment.objects.create(
            priority=1,
            cpu_required=4,
            gpu_required=1,
            cluster=self.cluster,
            ram_required=16 * 1024,
            image_path="docker://test/image",
        )

        self.allocation_service = ResourceAllocationService()

    def test_resource_allocation(self):
        """
        Test that resources are correctly allocated to a deployment
        """

        payload = ResourceAllocationRequestEntity(
            **{
                "cpu_allocated": 4,
                "gpu_allocated": 1,
                "ram_allocated": 16 * 1024,
                "cluster_id": self.cluster.id,
                "deployment_id": self.deployment.id,
            }
        )

        allocation = self.allocation_service.create(payload)

        self.assertEqual(allocation.cpu_allocated, 4)
        self.assertEqual(allocation.gpu_allocated, 1)
        self.assertEqual(allocation.ram_allocated, 16 * 1024)

        self.cluster.refresh_from_db()
        available_resources = self.cluster.available_resources()

        self.assertEqual(available_resources["gpu"], 3)
        self.assertEqual(available_resources["cpu"], 12)
        self.assertEqual(available_resources["ram"], 48 * 1024)

    @patch("core.services.deployment.RedisClient.z_add")
    def test_create_deployment_with_insufficient_resources(self, mock_z_add):
        """
        Test that deployment is added to Redis when there are insufficient resources.
        """

        # Simulating insufficient resources by reducing available GPU
        self.cluster.gpu = 0
        self.cluster.save()

        # Create the deployment request payload
        payload = NewDeploymentRequestEntity(
            priority=1,
            cpu_required=4,
            gpu_required=1,
            ram_required=16 * 1024,
            cluster_id=self.cluster.id,
            image_path="docker://test/image",
        )

        new_deployment = self.deployment_service.create(payload)

        # Ensuring that the Redis z_add method was called
        mock_z_add.assert_called_once_with(
            "DEPLOYMENT_QUEUE", {new_deployment.id: -new_deployment.priority}
        )

        # Deployment status should be QUEUED due to insufficient resources
        self.assertEqual(new_deployment.status, DeploymentStatus.QUEUED)


class TestDeploymentScheduling(TestCase):
    """
    Test Cases For Checking If High Priority Deployments Are Scheduled First.
    """

    def setUp(self) -> None:
        self.organization = Organization.objects.create(name="Test Organization")
        self.cluster = Cluster.objects.create(
            gpu=1,
            cpu=2,
            ram=2,
            name="Test Cluster",
            organization=self.organization,
        )

        self.deployment_service = DeploymentService()

    @patch("core.services.deployment.RedisClient.z_range_by_score")
    def test_high_priority_deployments_first(self, mock_z_range):
        """
        Test that high-priority deployments are scheduled before low-priority ones.
        """

        # Create deployments with different priorities
        deployments_data = [
            {
                "priority": 1,
                "cpu_required": 2,
                "gpu_required": 1,
                "ram_required": 4,
            },  # Highest priority
            {
                "priority": 3,
                "cpu_required": 1,
                "gpu_required": 1,
                "ram_required": 32,
            },  # Lowest priority
            {
                "priority": 2,
                "cpu_required": 1,
                "gpu_required": 1,
                "ram_required": 12,
            },  # Middle priority
        ]

        # Simulate creating deployments
        for data in deployments_data:
            payload = NewDeploymentRequestEntity(
                priority=data["priority"],
                cluster_id=self.cluster.id,
                image_path="docker://test/image",
                cpu_required=data["cpu_required"],
                gpu_required=data["gpu_required"],
                ram_required=data["ram_required"],
            )
            deployment = self.deployment_service.create(payload)

        # Mocking Redis queue return order (sorted by score = -priority)
        mock_z_range.return_value = [1, 2, 3]

        # Deployment IDs from Redis queue (mocked)
        deployment_ids_in_redis = mock_z_range(
            self.deployment_service._DeploymentService__redis_client,
            "DEPLOYMENT_QUEUE",
            "-inf",
            "+inf",
        )

        # Returned IDs should be in expected priority order
        self.assertEqual(deployment_ids_in_redis, [1, 2, 3])

        # All deployments should be queued
        deployments = Deployment.objects.filter(cluster=self.cluster)
        for deployment in deployments:
            self.assertEqual(deployment.status, DeploymentStatus.QUEUED)
