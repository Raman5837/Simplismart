from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet

from core.errors import BadRequestError, ResourceDoesNotExistsError
from core.models.organization import InviteCode, Membership
from core.types.request import MembershipRequestEntity


class MembershipService:
    """
    Service Layer For Membership
    """

    @transaction.atomic
    def create(self, user: User, payload: MembershipRequestEntity) -> Membership:
        """
        Creates new `Membership`
        """

        try:
            invite_code = InviteCode.objects.select_related("organization").get(
                code=payload.invite_code, is_active=True
            )
        except InviteCode.DoesNotExist as exception:
            raise ResourceDoesNotExistsError("Invite Code does not exists") from exception

        # NOTE: Not checking at role level
        if Membership.objects.filter(user=user, organization=invite_code.organization).exists():
            return BadRequestError("You are already associated with the organization")

        # New membership
        membership = Membership.objects.create(
            user=user,
            role=payload.role,
            organization=invite_code.organization,
        )
        # NOTE: If `invite_code` is for one time use, mark it in-active

        return membership

    def list(self) -> QuerySet[Membership]:
        """
        Returns all `Membership`
        """

        return Membership.objects.all()

    def get(self, membership_id: str) -> Membership:
        """
        Returns `Membership` if exists
        """

        try:
            return Membership.objects.get(id=membership_id)
        except Exception as exception:
            raise ResourceDoesNotExistsError("Membership does not exists") from exception
