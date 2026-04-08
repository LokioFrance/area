from rest_framework.viewsets import ModelViewSet

from zone.models import Area, SubArea

from .serializers import AreaSerializer, SubAreaSerializer


class AreaViewSet(ModelViewSet):
    """
    CRUD complet pour les zones géographiques.

    list:   GET  /api/areas/
    create: POST /api/areas/
    retrieve: GET  /api/areas/{id}/
    update: PUT  /api/areas/{id}/
    partial_update: PATCH /api/areas/{id}/
    destroy: DELETE /api/areas/{id}/
    """

    queryset = Area.objects.prefetch_related("sub_areas").all()
    serializer_class = AreaSerializer


class SubAreaViewSet(ModelViewSet):
    """
    CRUD complet pour les sous-zones.

    list:   GET  /api/sub-areas/
    create: POST /api/sub-areas/
    retrieve: GET  /api/sub-areas/{id}/
    update: PUT  /api/sub-areas/{id}/
    partial_update: PATCH /api/sub-areas/{id}/
    destroy: DELETE /api/sub-areas/{id}/
    """

    queryset = SubArea.objects.select_related("area").all()
    serializer_class = SubAreaSerializer
