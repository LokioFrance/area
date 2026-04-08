from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from zone.models import Area, SubArea


class AreaTests(APITestCase):
    """Tests CRUD pour le endpoint /api/areas/."""

    def setUp(self):
        self.area = Area.objects.create(name="Entrepôt Nord", address="12 rue des Lilas, 75001 Paris")

    # ── LIST ──────────────────────────────────────────────────────────────────

    def test_list_areas(self):
        response = self.client.get(reverse("area-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # ── CREATE ────────────────────────────────────────────────────────────────

    def test_create_area(self):
        payload = {"name": "Entrepôt Sud", "address": "8 avenue des Roses, 69001 Lyon"}
        response = self.client.post(reverse("area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Area.objects.count(), 2)
        self.assertEqual(response.data["name"], "Entrepôt Sud")

    def test_create_area_missing_name(self):
        payload = {"address": "8 avenue des Roses, 69001 Lyon"}
        response = self.client.post(reverse("area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_area_missing_address(self):
        payload = {"name": "Entrepôt Sud"}
        response = self.client.post(reverse("area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_area_duplicate_address(self):
        payload = {"name": "Autre nom", "address": "12 rue des Lilas, 75001 Paris"}
        response = self.client.post(reverse("area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── RETRIEVE ──────────────────────────────────────────────────────────────

    def test_retrieve_area(self):
        response = self.client.get(reverse("area-detail", args=[self.area.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.area.name)
        self.assertIn("sub_areas", response.data)

    def test_retrieve_area_not_found(self):
        response = self.client.get(reverse("area-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def test_update_area(self):
        payload = {"name": "Entrepôt Nord (renommé)", "address": "12 rue des Lilas, 75001 Paris"}
        response = self.client.put(reverse("area-detail", args=[self.area.id]), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.area.refresh_from_db()
        self.assertEqual(self.area.name, "Entrepôt Nord (renommé)")

    def test_partial_update_area(self):
        response = self.client.patch(
            reverse("area-detail", args=[self.area.id]),
            {"name": "Entrepôt Nord v2"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.area.refresh_from_db()
        self.assertEqual(self.area.name, "Entrepôt Nord v2")

    # ── DELETE ────────────────────────────────────────────────────────────────

    def test_delete_area(self):
        response = self.client.delete(reverse("area-detail", args=[self.area.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Area.objects.count(), 0)

    def test_delete_area_cascades_to_sub_areas(self):
        SubArea.objects.create(area=self.area, name="Rayon A")
        self.client.delete(reverse("area-detail", args=[self.area.id]))
        self.assertEqual(SubArea.objects.count(), 0)


class SubAreaTests(APITestCase):
    """Tests CRUD pour le endpoint /api/sub-areas/."""

    def setUp(self):
        self.area = Area.objects.create(name="Entrepôt Nord", address="12 rue des Lilas, 75001 Paris")
        self.sub_area = SubArea.objects.create(area=self.area, name="Rayon A")

    # ── LIST ──────────────────────────────────────────────────────────────────

    def test_list_sub_areas(self):
        response = self.client.get(reverse("sub-area-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # ── CREATE ────────────────────────────────────────────────────────────────

    def test_create_sub_area(self):
        payload = {"name": "Rayon B", "area": self.area.id}
        response = self.client.post(reverse("sub-area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubArea.objects.count(), 2)

    def test_create_sub_area_missing_area(self):
        payload = {"name": "Rayon B"}
        response = self.client.post(reverse("sub-area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sub_area_invalid_area(self):
        payload = {"name": "Rayon B", "area": 9999}
        response = self.client.post(reverse("sub-area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── RETRIEVE ──────────────────────────────────────────────────────────────

    def test_retrieve_sub_area(self):
        response = self.client.get(reverse("sub-area-detail", args=[self.sub_area.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Rayon A")
        self.assertEqual(response.data["area"], self.area.id)

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def test_update_sub_area(self):
        payload = {"name": "Rayon A (renommé)", "area": self.area.id}
        response = self.client.put(reverse("sub-area-detail", args=[self.sub_area.id]), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sub_area.refresh_from_db()
        self.assertEqual(self.sub_area.name, "Rayon A (renommé)")

    # ── DELETE ────────────────────────────────────────────────────────────────

    def test_delete_sub_area(self):
        response = self.client.delete(reverse("sub-area-detail", args=[self.sub_area.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SubArea.objects.count(), 0)

    def test_delete_sub_area_does_not_delete_parent(self):
        self.client.delete(reverse("sub-area-detail", args=[self.sub_area.id]))
        self.assertEqual(Area.objects.count(), 1)

    # ── NESTED (area expose ses sub_areas) ───────────────────────────────────

    def test_area_exposes_sub_areas(self):
        response = self.client.get(reverse("area-detail", args=[self.area.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["sub_areas"]), 1)
        self.assertEqual(response.data["sub_areas"][0]["name"], "Rayon A")
