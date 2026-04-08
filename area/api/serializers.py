from rest_framework import serializers

from zone.models import Area, SubArea


class SubAreaSerializer(serializers.ModelSerializer):
    """Sérialise une sous-zone (id, name, area)."""

    class Meta:
        model = SubArea
        fields = ["id", "name", "area"]


class AreaSerializer(serializers.ModelSerializer):
    """Sérialise une zone avec ses sous-zones imbriquées (lecture seule)."""

    sub_areas = SubAreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ["id", "name", "address", "sub_areas"]
