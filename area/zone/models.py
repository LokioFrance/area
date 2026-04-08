from django.db import models


class Area(models.Model):
    """Zone géographique principale (ex : entrepôt, bâtiment, site)."""

    name = models.CharField(max_length=100, verbose_name="Nom")
    address = models.CharField(max_length=255, unique=True, verbose_name="Adresse")

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubArea(models.Model):
    """Sous-zone appartenant à une Area (ex : rayon, salle, couloir)."""

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="sub_areas",
        verbose_name="Zone parente",
    )
    name = models.CharField(max_length=100, verbose_name="Nom")

    class Meta:
        verbose_name = "Sous-zone"
        verbose_name_plural = "Sous-zones"
        ordering = ["name"]

    def __str__(self):
        return f"{self.area.name} › {self.name}"
