"""
Serveur MCP pour le microservice Area.

Expose les outils suivants à tout client MCP (Claude, etc.) :
  - list_areas        : lister toutes les zones
  - get_area          : détail d'une zone (avec ses sous-zones)
  - create_area       : créer une zone
  - update_area       : modifier une zone
  - delete_area       : supprimer une zone (cascade sur ses sous-zones)
  - list_sub_areas        : lister toutes les sous-zones
  - get_sub_area          : détail d'une sous-zone
  - create_sub_area       : créer une sous-zone dans une zone
  - update_sub_area       : modifier une sous-zone
  - delete_sub_area       : supprimer une sous-zone
  - get_honeypot_attempts : lister les tentatives enregistrées par le honeypot /admin/

Transport : SSE (HTTP) — le serveur écoute sur 0.0.0.0:${MCP_PORT}.

Variables d'environnement requises :
  AREA_API_URL     : URL de base de l'API area (ex: http://area:8000)
  MCP_PORT         : port d'écoute du serveur MCP (défaut: 9000)
  MCP_API_KEY      : clé partagée attendue dans l'en-tête X-MCP-Key (optionnel)
  HONEYPOT_API_KEY : clé pour accéder à GET /api/honeypot/ (doit correspondre au .env de area)
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

# ── Configuration ─────────────────────────────────────────────────────────────

AREA_API_URL = os.environ.get("AREA_API_URL", "http://area:8000").rstrip("/")
MCP_PORT = int(os.environ.get("MCP_PORT", "9000"))
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
HONEYPOT_API_KEY = os.environ.get("HONEYPOT_API_KEY", "")

mcp = FastMCP(
    name="area-mcp",
    instructions=(
        "Serveur MCP du microservice Area. "
        "Permet de gérer les zones géographiques (Area) et leurs sous-zones (SubArea). "
        "Chaque Area possède un nom et une adresse unique. "
        "Chaque SubArea appartient à une Area et possède un nom. "
        "Donne également accès aux tentatives honeypot enregistrées sur /admin/."
    ),
)


# ── Client HTTP ───────────────────────────────────────────────────────────────

def _client() -> httpx.Client:
    """Retourne un client HTTP configuré vers l'API area."""
    return httpx.Client(base_url=AREA_API_URL, timeout=10.0)


def _check(response: httpx.Response) -> dict | list | None:
    """Lève une exception lisible en cas d'erreur HTTP."""
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise ValueError(
            f"Erreur API {e.response.status_code} : {e.response.text}"
        ) from e
    if response.status_code == 204:
        return None
    return response.json()


# ── OUTILS — AREA ─────────────────────────────────────────────────────────────

@mcp.tool()
def list_areas() -> list:
    """Liste toutes les zones géographiques avec leurs sous-zones."""
    with _client() as c:
        return _check(c.get("/api/areas/"))


@mcp.tool()
def get_area(area_id: int) -> dict:
    """
    Retourne le détail d'une zone, y compris ses sous-zones.

    Args:
        area_id: Identifiant de la zone.
    """
    with _client() as c:
        return _check(c.get(f"/api/areas/{area_id}/"))


@mcp.tool()
def create_area(name: str, address: str) -> dict:
    """
    Crée une nouvelle zone géographique.

    Args:
        name:    Nom de la zone (ex: "Entrepôt Nord").
        address: Adresse physique unique (ex: "12 rue des Lilas, 75001 Paris").
    """
    with _client() as c:
        return _check(c.post("/api/areas/", json={"name": name, "address": address}))


@mcp.tool()
def update_area(area_id: int, name: str, address: str) -> dict:
    """
    Met à jour une zone existante.

    Args:
        area_id: Identifiant de la zone à modifier.
        name:    Nouveau nom.
        address: Nouvelle adresse.
    """
    with _client() as c:
        return _check(
            c.put(f"/api/areas/{area_id}/", json={"name": name, "address": address})
        )


@mcp.tool()
def delete_area(area_id: int) -> str:
    """
    Supprime une zone et toutes ses sous-zones (cascade).

    Args:
        area_id: Identifiant de la zone à supprimer.
    """
    with _client() as c:
        _check(c.delete(f"/api/areas/{area_id}/"))
    return f"Zone {area_id} supprimée."


# ── OUTILS — SUB-AREA ─────────────────────────────────────────────────────────

@mcp.tool()
def list_sub_areas() -> list:
    """Liste toutes les sous-zones de toutes les zones."""
    with _client() as c:
        return _check(c.get("/api/sub-areas/"))


@mcp.tool()
def get_sub_area(sub_area_id: int) -> dict:
    """
    Retourne le détail d'une sous-zone.

    Args:
        sub_area_id: Identifiant de la sous-zone.
    """
    with _client() as c:
        return _check(c.get(f"/api/sub-areas/{sub_area_id}/"))


@mcp.tool()
def create_sub_area(name: str, area_id: int) -> dict:
    """
    Crée une sous-zone dans une zone existante.

    Args:
        name:    Nom de la sous-zone (ex: "Rayon A").
        area_id: Identifiant de la zone parente.
    """
    with _client() as c:
        return _check(
            c.post("/api/sub-areas/", json={"name": name, "area": area_id})
        )


@mcp.tool()
def update_sub_area(sub_area_id: int, name: str, area_id: int) -> dict:
    """
    Met à jour une sous-zone existante.

    Args:
        sub_area_id: Identifiant de la sous-zone à modifier.
        name:        Nouveau nom.
        area_id:     Identifiant de la zone parente (peut rester le même).
    """
    with _client() as c:
        return _check(
            c.put(
                f"/api/sub-areas/{sub_area_id}/",
                json={"name": name, "area": area_id},
            )
        )


@mcp.tool()
def delete_sub_area(sub_area_id: int) -> str:
    """
    Supprime une sous-zone (la zone parente n'est pas affectée).

    Args:
        sub_area_id: Identifiant de la sous-zone à supprimer.
    """
    with _client() as c:
        _check(c.delete(f"/api/sub-areas/{sub_area_id}/"))
    return f"Sous-zone {sub_area_id} supprimée."


# ── OUTILS — HONEYPOT ────────────────────────────────────────────────────────

@mcp.tool()
def get_honeypot_attempts() -> list:
    """
    Retourne toutes les tentatives enregistrées par le honeypot /admin/.

    Chaque entrée contient : ip, user_agent, path, method, username, timestamp.
    Nécessite que HONEYPOT_API_KEY soit configurée sur le microservice.
    """
    with _client() as c:
        return _check(
            c.get("/api/honeypot/", headers={"X-Honeypot-Key": HONEYPOT_API_KEY})
        )


# ── Entrée ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="sse")
