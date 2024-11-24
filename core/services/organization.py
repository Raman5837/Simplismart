from django.db import transaction
from django.db.models import QuerySet

from core.errors import ResourceDoesNotExistsError
from core.models.organization import InviteCode, Organization
from core.types.request import OrganizationRequestEntity


class OrganizationService:
    """
    Service Layer For Organization
    """

    @transaction.atomic
    def create(self, payload: OrganizationRequestEntity) -> Organization:
        """
        Creates new `Organization`
        """

        organization = Organization.objects.create(name=payload.name)

        # Also creating an invite code for this organization
        InviteCode.objects.create(organization=organization)

        return organization

    def list(self) -> QuerySet[Organization]:
        """
        Returns all `Organization`
        """

        return Organization.objects.all()

    def get(self, organization_id: str) -> Organization:
        """
        Returns `Organization` if exists
        """

        try:
            return Organization.objects.get(id=organization_id)
        except Exception as exception:
            raise ResourceDoesNotExistsError(
                "Organization does not exists"
            ) from exception
