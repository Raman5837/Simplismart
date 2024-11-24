from json import dumps

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Cluster, Deployment, Organization
from core.services.resource import ResourceAllocationService
from core.types.request import ResourceAllocationRequestEntity


class LoginTestCase(TestCase):
    """ """

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
    """ """

    def setUp(self) -> None:
        self.organization = Organization.objects.create(name="Test Organization 1")
        self.cluster = Cluster.objects.create(
            gpu=4,
            cpu=16,
            ram=64 * 1024,
            name="Test Cluster",
            organization=self.organization,
        )

        # Create a deployment
        self.deployment = Deployment.objects.create(
            priority=1,
            cpu_required=4,
            gpu_required=1,
            cluster=self.cluster,
            ram_required=16 * 1024,
            image_path="docker://test/image",
        )

        self.service = ResourceAllocationService()

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

        allocation = self.service.create(payload)

        self.assertEqual(allocation.cpu_allocated, 4)
        self.assertEqual(allocation.gpu_allocated, 1)
        self.assertEqual(allocation.ram_allocated, 16 * 1024)

        self.cluster.refresh_from_db()
        available_resources = self.cluster.available_resources()

        self.assertEqual(available_resources["gpu"], 3)
        self.assertEqual(available_resources["cpu"], 12)
        self.assertEqual(available_resources["ram"], 48 * 1024)
