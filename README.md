# Area — Microservice de gestion des zones

Le microservice **Area** est la brique de base de Lokio. Il gère les emplacements physiques dans lesquels sont rangés les objets inventoriés.

Une zone représente un site physique (bâtiment, entrepôt, étage, pièces…), identifié par un nom et une adresse unique. Chaque zone peut contenir plusieurs sous-zones (pièces, rayons, étagères…). Les autres microservices (Boxify, Marko) s'appuient sur ces zones pour indiquer où sont les boîtes et les objets.

Le microservice expose une API REST sécurisée par JWT, et un serveur MCP permettant aux LLM de consulter et manipuler les zones directement en langage naturel.

---

## Stack

| Composant | Version |
|---|---|
| Python | 3.12 |
| Django | 6.0 |
| Django REST Framework | 3.16.1 |
| SimpleJWT | 5.5.1 |
| drf-yasg (Swagger) | 1.21.10 |
| FastMCP | — |
| Gunicorn | — |

---

## Installation

### Avec Docker (recommandé)

**Prérequis :** Docker et Docker Compose installés.

```bash
./deploy.sh
```

Le script `deploy.sh` fait tout automatiquement :

1. Vérifie que Docker est disponible
2. Crée le `.env` depuis `.env.example` si absent et ouvre l'éditeur pour le remplir
3. Valide que `DJANGO_SECRET_KEY` est bien définie
4. Build l'image et démarre les conteneurs (`area` + `area-mcp`)
5. Attend que les services soient sains et affiche les URLs

> Au premier démarrage, créer le superutilisateur Django :
> ```bash
> docker compose exec area python manage.py createsuperuser
> ```

Pour arrêter les services :

```bash
docker compose down
```

---

### Sans Docker (développement local)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd area
cp ../.env.example ../.env
# Remplir les valeurs dans .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

L'API est accessible sur `http://localhost:8001`.

---

## Variables d'environnement

Copier `.env.example` en `.env` et remplir les valeurs. Ne jamais committer `.env`.

| Variable | Description | Exemple |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clé secrète Django (générer avec `secrets.token_urlsafe(50)`) | — |
| `DJANGO_DEBUG` | Mode debug (`true` en dev, `false` en prod) | `false` |
| `DJANGO_ALLOWED_HOSTS` | Hosts autorisés, séparés par des virgules | `localhost,127.0.0.1` |
| `DJANGO_ADMIN_URL` | URL secrète de la vraie interface admin (sans `/`) | `mon-panneau-secret` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Durée de vie du token d'accès (minutes) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Durée de vie du token de rafraîchissement (jours) | `7` |
| `HONEYPOT_API_KEY` | Clé partagée pour protéger `GET /api/honeypot/` | — |
| `GUNICORN_WORKERS` | Nombre de workers Gunicorn (règle : 2×CPU+1) | `3` |
| `GUNICORN_TIMEOUT` | Timeout des requêtes en secondes | `30` |
| `HOST_PORT` | Port exposé sur l'hôte pour l'API | `8001` |
| `MCP_PORT` | Port interne du serveur MCP (dans le conteneur) | `9000` |
| `MCP_HOST_PORT` | Port exposé sur l'hôte pour le serveur MCP | `9001` |
| `MCP_API_KEY` | Clé optionnelle pour sécuriser l'accès MCP | — |

---

## Endpoints API

Toutes les routes sont préfixées par `/api/`.

### Zones (Area)

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/areas/` | Liste toutes les zones (avec leurs sous-zones) |
| `POST` | `/api/areas/` | Crée une zone |
| `GET` | `/api/areas/{id}/` | Détail d'une zone |
| `PUT` / `PATCH` | `/api/areas/{id}/` | Modifie une zone |
| `DELETE` | `/api/areas/{id}/` | Supprime une zone (cascade sur ses sous-zones) |

### Sous-zones (SubArea)

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/sub-areas/` | Liste toutes les sous-zones |
| `POST` | `/api/sub-areas/` | Crée une sous-zone |
| `GET` | `/api/sub-areas/{id}/` | Détail d'une sous-zone |
| `PUT` / `PATCH` | `/api/sub-areas/{id}/` | Modifie une sous-zone |
| `DELETE` | `/api/sub-areas/{id}/` | Supprime une sous-zone |

### Authentification JWT

| Méthode | URL | Description |
|---|---|---|
| `POST` | `/api/token/` | Obtenir un token d'accès et de rafraîchissement |
| `POST` | `/api/token/refresh/` | Rafraîchir un token d'accès |

### Sécurité — Honeypot

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/honeypot/` | Liste les tentatives enregistrées par le honeypot |

> Cet endpoint est protégé par l'en-tête `X-Honeypot-Key: <HONEYPOT_API_KEY>`.  
> Il est utilisé par l'UI Lokio pour agréger les tentatives de tous les microservices.

---

## Documentation interactive

Une fois le serveur lancé :

| Interface | URL |
|---|---|
| Swagger UI | `http://localhost:8001/swagger/` |
| ReDoc | `http://localhost:8001/redoc/` |
| JSON (OpenAPI) | `http://localhost:8001/swagger.json` |

---

## Sécurité — Honeypot

L'URL `/admin/` est un **honeypot** : elle affiche une fausse page de connexion Django identique à la vraie. Toute tentative d'accès (GET ou POST) est enregistrée en base de données et dans le fichier `honeypot.log` avec l'IP source, le User-Agent, les identifiants soumis et l'horodatage.

La **vraie interface d'administration** est disponible à l'URL secrète définie dans `DJANGO_ADMIN_URL`. Ce chemin doit être difficile à deviner (utiliser un token aléatoire).

```bash
# Générer une URL admin secrète
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## Serveur MCP

Le microservice inclut un **serveur MCP (Model Context Protocol)** qui permet à Claude (ou tout client MCP compatible) d'interagir avec l'API Area en langage naturel.

### Démarrage

Avec Docker, le serveur MCP démarre automatiquement avec `docker compose up`. Il est accessible via SSE sur :

```
http://localhost:9001/sse
```

### Outils disponibles

| Outil | Description |
|---|---|
| `list_areas` | Liste toutes les zones avec leurs sous-zones |
| `get_area` | Détail d'une zone |
| `create_area` | Crée une zone |
| `update_area` | Modifie une zone |
| `delete_area` | Supprime une zone (cascade) |
| `list_sub_areas` | Liste toutes les sous-zones |
| `get_sub_area` | Détail d'une sous-zone |
| `create_sub_area` | Crée une sous-zone dans une zone |
| `update_sub_area` | Modifie une sous-zone |
| `delete_sub_area` | Supprime une sous-zone |
| `get_honeypot_attempts` | Liste les tentatives enregistrées par le honeypot |

### Configurer le client MCP

Ajouter dans la configuration du Client MCP :

```json
{
  "mcpServers": {
    "area": {
      "type": "sse",
      "url": "http://localhost:9001/sse"
    }
  }
}
```

Si `MCP_API_KEY` est définie, ajouter l'en-tête `X-MCP-Key` dans la configuration de votre client MCP.

---

## Tests

```bash
cd area
python manage.py test api.tests --verbosity=2
```

20 tests unitaires couvrant :

- `AreaTests` : list, create (avec et sans champ manquant), retrieve (avec 404), update, partial_update, delete, cascade sur les sous-zones
- `SubAreaTests` : list, create (avec FK invalide et champ manquant), retrieve, update, partial_update, delete, vérification que la zone parente n'est pas supprimée

---

## Linter

```bash
ruff check area/
```

---

## Auteur

Projet **Lokio** — développé par **Clément Chermeux**.

---

## Améliorations futures

- [ ] Authentification sur les endpoints MCP via `MCP_API_KEY` (middleware SSE)
- [ ] Pagination des résultats sur `/api/areas/` et `/api/sub-areas/`
- [ ] Filtrage et recherche sur les zones par nom ou adresse
- [ ] Export CSV / JSON des tentatives honeypot
- [ ] Assigner des zones à des personnes, pouvoir diviser des sous-zones en sous-sous-zones etc
- [ ] Mettre en place le CI/CD
- [ ] Mettre en place le systeme de connexion commune de l'ensemble de la soltion lokio


