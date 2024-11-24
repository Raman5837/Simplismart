from rest_framework import serializers


from core.models.deployment import Deployment


class DeploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = "__all__"
