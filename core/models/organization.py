from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from core.constants import UserRole
from core.models.abstract import AbstractModel


class Organization(AbstractModel):
    """
    Stores all organizations.
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"<Organization> {self.name}"


class Membership(AbstractModel):
    """
    User and organization membership.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=UserRole.choices)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"<Membership> {self.user} - {self.role}"


class InviteCode(AbstractModel):
    """
    Invite codes linked to organizations for user membership.
    """

    is_active = models.BooleanField(default=True)
    code = models.UUIDField(default=uuid4, editable=False, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="invite_codes")

    def __str__(self) -> str:
        return f"<InviteCode> {self.code}"
