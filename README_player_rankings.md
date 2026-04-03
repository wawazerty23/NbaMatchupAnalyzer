# Extraction des classements de joueurs Basketball Monster

Ce script Python extrait les données des joueurs depuis la page `https://basketballmonster.com/playerrankings.aspx` et les retourne au format JSON.

## Prérequis

- Python 3.6+
- Les bibliothèques `requests` et `beautifulsoup4`

## Installation

1. Activez l'environnement virtuel (si présent) :
   ```bash
   source venv/bin/activate
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
   Ou installez manuellement :
   ```bash
   pip install requests beautifulsoup4
   ```

## Utilisation

Exécutez le script sans argument pour récupérer **tous les joueurs** (filtre "All Players" activé) :
```bash
python scrape_player_rankings.py
```

Pour récupérer uniquement les **Top Players** (comportement par défaut du site) :
```bash
python scrape_player_rankings.py --top-only
```

Options disponibles :
- `--top-only` : extrait seulement les joueurs les mieux classés (environ 188 joueurs)
- `--output FILE` : spécifie le fichier de sortie (par défaut `player_rankings.json`)

Le script va :
1. Récupérer la page web
2. Si `--top-only` n'est pas spécifié, envoyer une requête POST pour activer le filtre "All Players"
3. Parser le tableau des classements
4. Extraire les données de chaque joueur
5. Générer un fichier JSON dans le répertoire courant

## Structure des données

Le fichier JSON contient une liste d'objets, chaque objet représentant un joueur avec les attributs suivants :

| Champ | Type | Description |
|-------|------|-------------|
| round | integer | Round de draft |
| rank | integer | Rang global |
| value | float | Valeur totale du joueur |
| name | string | Nom du joueur |
| team | string | Équipe (code à 3 lettres) |
| pos | string | Position (C, F, G) |
| inj | string/null | Statut de blessure (généralement null) |
| games | integer | Nombre de matchs joués |
| minutes_per_game | float | Minutes par match |
| points_per_game | float | Points par match |
| threes_per_game | float | Trois points par match |
| rebounds_per_game | float | Rebonds par match |
| assists_per_game | float | Passes décisives par match |
| steals_per_game | float | Interceptions par match |
| blocks_per_game | float | Contres par match |
| fg_percent | float | Pourcentage de tirs réussis |
| fga_per_game | float | Tentatives de tirs par match |
| ft_percent | float | Pourcentage de lancers francs |
| fta_per_game | float | Tentatives de lancers francs par match |
| turnovers_per_game | float | Pertes de balle par match |
| usage | float | Usage du joueur (%) |
| points_value | float | Valeur des points |
| threes_value | float | Valeur des trois points |
| rebounds_value | float | Valeur des rebonds |
| assists_value | float | Valeur des passes |
| steals_value | float | Valeur des interceptions |
| blocks_value | float | Valeur des contres |
| fg_percent_value | float | Valeur du pourcentage de tirs |
| ft_percent_value | float | Valeur du pourcentage de lancers francs |
| turnovers_value | float | Valeur des pertes de balle (négative) |
| player_id | integer | ID unique du joueur sur Basketball Monster |

## Exemple de sortie

```json
[
  {
    "round": 1,
    "rank": 1,
    "value": 1.09,
    "name": "Nikola Jokic",
    "team": "DEN",
    "pos": "C",
    "inj": null,
    "games": 61,
    "minutes_per_game": 34.9,
    "points_per_game": 27.7,
    "threes_per_game": 1.8,
    "rebounds_per_game": 13.0,
    "assists_per_game": 10.8,
    "steals_per_game": 1.4,
    "blocks_per_game": 0.8,
    "fg_percent": 0.572,
    "fga_per_game": 17.3,
    "ft_percent": 0.826,
    "fta_per_game": 7.3,
    "turnovers_per_game": 3.9,
    "usage": 31.0,
    "points_value": 1.9,
    "threes_value": 0.08,
    "rebounds_value": 2.99,
    "assists_value": 3.44,
    "steals_value": 0.95,
    "blocks_value": 0.2,
    "fg_percent_value": 2.23,
    "ft_percent_value": 0.48,
    "turnovers_value": -2.44,
    "player_id": 3930
  },
  ...
]
```

## Intégration avec d'autres scripts

Le fichier JSON peut être importé dans d'autres scripts Python :

```python
import json
with open('player_rankings.json', 'r') as f:
    players = json.load(f)
```

## Intégration FastAPI

Le script `scrape_player_rankings.py` a été intégré à l'application FastAPI `NbaMatchupAnalyzer`. Un nouvel endpoint `/player_rankings` est disponible pour récupérer les classements des joueurs via une API REST.

### Utilisation de l'API

L'API expose les endpoints suivants :

- `GET /player_rankings` : Retourne les classements des joueurs.
  - Paramètres query :
    - `all_players` (bool, défaut `true`) : Si `true`, récupère tous les joueurs. Si `false`, seulement les meilleurs.
    - `force_refresh` (bool, défaut `false`) : Force le rafraîchissement des données (ignore le cache).
    - `use_file_cache` (bool, défaut `true`) : Utilise le fichier cache si le cache mémoire est vide.
- `GET /player_status` : Retourne la liste des joueurs blessés (existant).
- `GET /health` : Vérification de l'état de l'API.

### Exemple de requête

```bash
curl "http://localhost:8000/player_rankings?all_players=true"
```

### Cache

L'API implémente un cache en mémoire avec un timeout de 5 minutes pour éviter de surcharger le site source. Les données sont également sauvegardées dans le fichier `player_rankings.json` pour une persistence entre les redémarrages.

### Démarrage de l'API

Pour démarrer l'API FastAPI :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ou utilisez le Dockerfile fourni.

## Notes

- Le script dépend de la structure HTML de la page Basketball Monster. Si celle‑ci change, le script peut nécessiter des ajustements.
- Les données sont extraites en temps réel, reflétant les statistiques actuelles de la saison.
- Le script inclut une gestion d'erreurs basique et des en‑têtes HTTP pour éviter les blocages.

## Licence

Ce script est fourni à titre éducatif. Veuillez respecter les conditions d'utilisation du site Basketball Monster.