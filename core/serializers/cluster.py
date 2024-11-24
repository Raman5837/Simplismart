from rest_framework import serializers

from core.models.resource import Cluster, ResourceAllocation


class ClusterSerializer(serializers.ModelSerializer):
    available_resources = serializers.ReadOnlyField(source="available_resources")

    class Meta:
        model = Cluster
        fields = "__all__"


class ResourceAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAllocation
        fields = "__all__"
