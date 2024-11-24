from rest_framework import serializers

from core.models.organization import InviteCode, Membership, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """ """

    invite_code = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "created_at", "updated_at", "invite_code"]

    def get_invite_code(self, instance: Organization):
        """
        Retrieves the invite code associated with the organization.
        Assumes there is at least one active invite code for the organization.
        """

        invite_code = InviteCode.objects.filter(organization=instance, is_active=True).first()

        return str(invite_code.code) if invite_code else None


class MembershipSerializer(serializers.ModelSerializer):
    """ """

    class Meta:
        model = Membership
        fields = "__all__"
