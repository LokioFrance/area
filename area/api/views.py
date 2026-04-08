import os

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from zone.models import Area, SubArea

from api.models import HoneypotAttempt

from .serializers import AreaSerializer, HoneypotAttemptSerializer, SubAreaSerializer


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


class HoneypotView(APIView):
    """
    GET /api/honeypot/

    Retourne toutes les tentatives enregistrées par le honeypot.
    Protégé par l'en-tête X-Honeypot-Key (valeur = HONEYPOT_API_KEY).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        expected_key = os.environ.get("HONEYPOT_API_KEY", "")
        if not expected_key:
            return Response(
                {"detail": "HONEYPOT_API_KEY non configurée sur ce service."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        provided_key = request.headers.get("X-Honeypot-Key", "")
        if provided_key != expected_key:
            return Response(
                {"detail": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN
            )

        attempts = HoneypotAttempt.objects.all()
        serializer = HoneypotAttemptSerializer(attempts, many=True)
        return Response(serializer.data)
