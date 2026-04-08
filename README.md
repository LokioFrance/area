# Area — Microservice de gestion des zones

Microservice REST responsable de la hiérarchie des emplacements physiques :

**Zone (Area)** → **Sous-zone (SubArea)**.

## Stack

| Composant | Version |
|---|---|
| Python | 3.12 |
| Django | 6.0 |
| Django REST Framework | 3.16.1 |
| SimpleJWT | 5.5.1 |
| drf-yasg (Swagger) | 1.21.10 |

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd area
python manage.py migrate
python manage.py runserver 8001
```

## Endpoints

| Méthode | URL | Description |
|---|---|---|
| GET | `/api/areas/` | Liste toutes les zones |
| POST | `/api/areas/` | Crée une zone |
| GET | `/api/areas/{id}/` | Détail d'une zone (avec sous-zones) |
| PUT/PATCH | `/api/areas/{id}/` | Modifie une zone |
| DELETE | `/api/areas/{id}/` | Supprime une zone (cascade sur ses sous-zones) |
| GET | `/api/sub-areas/` | Liste toutes les sous-zones |
| POST | `/api/sub-areas/` | Crée une sous-zone |
| GET | `/api/sub-areas/{id}/` | Détail d'une sous-zone |
| PUT/PATCH | `/api/sub-areas/{id}/` | Modifie une sous-zone |
| DELETE | `/api/sub-areas/{id}/` | Supprime une sous-zone |
| POST | `/api/token/` | Obtenir un token JWT |
| POST | `/api/token/refresh/` | Rafraîchir un token JWT |

## Documentation interactive

Une fois le serveur lancé :

- Swagger UI : `http://localhost:8001/swagger/`
- ReDoc : `http://localhost:8001/redoc/`
- JSON : `http://localhost:8001/swagger.json`

## Tests

```bash
cd area
python manage.py test api.tests --verbosity=2
```

20 tests couvrant : list, create, retrieve, update, partial_update, delete pour Area et SubArea, + cas d'erreur (champ manquant, adresse dupliquée, FK invalide, cascade).

## Linter

```bash
ruff check area/
```
