from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import time
import json
import os

from players_status import get_injured_players
from scrape_player_rankings import fetch_player_rankings


app = FastAPI(
    title="NBA Matchup Analyzer API",
    description="API pour les données NBA: blessures et classements des joueurs",
    version="1.0.0",
)

# Cache en mémoire
_player_rankings_cache = {
    "data": None,
    "timestamp": 0,
    "all_players": True,
}
CACHE_TIMEOUT = 300  # 5 minutes en secondes
CACHE_FILE = "player_rankings.json"


def get_player_rankings_cached(all_players: bool = True, force_refresh: bool = False):
    """
    Récupère les classements avec cache.
    """
    global _player_rankings_cache
    
    current_time = time.time()
    
    # Vérifier si le cache est valide (mêmes paramètres et pas expiré)
    if not force_refresh and _player_rankings_cache["data"] is not None:
        if _player_rankings_cache["all_players"] == all_players:
            if current_time - _player_rankings_cache["timestamp"] < CACHE_TIMEOUT:
                return _player_rankings_cache["data"]
    
    # Si le cache est invalide, scraper
    rankings = fetch_player_rankings(all_players=all_players)
    
    # Mettre à jour le cache
    _player_rankings_cache["data"] = rankings
    _player_rankings_cache["timestamp"] = current_time
    _player_rankings_cache["all_players"] = all_players
    
    # Sauvegarder dans un fichier pour une persistence basique
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(rankings, f, indent=2)
    except Exception:
        pass  # Ignorer les erreurs d'écriture de fichier
    
    return rankings


def load_player_rankings_from_file():
    """
    Charge les classements depuis le fichier cache.
    """
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None


@app.get("/player_status", summary="Liste des joueurs blessés")
def read_player_status():
    try:
        injured_players = get_injured_players()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur de récupération: {exc}") from exc

    # Retour JSON brut pour garder la structure existante
    return JSONResponse(content=injured_players)


@app.get("/player_rankings", summary="Classements des joueurs")
def read_player_rankings(
    all_players: bool = Query(
        default=True,
        description="Si True, récupère tous les joueurs. Si False, seulement les meilleurs."
    ),
    force_refresh: bool = Query(
        default=False,
        description="Forcer le rafraîchissement des données (ignorer le cache)"
    ),
    use_file_cache: bool = Query(
        default=True,
        description="Utiliser le fichier cache si le cache mémoire est vide"
    )
):
    """
    Récupère les classements des joueurs depuis basketballmonster.com/playerrankings.aspx
    avec support de cache.
    """
    # Si force_refresh est False et use_file_cache est True, essayer de charger depuis le fichier
    if not force_refresh and use_file_cache and _player_rankings_cache["data"] is None:
        file_data = load_player_rankings_from_file()
        if file_data is not None:
            _player_rankings_cache["data"] = file_data
            _player_rankings_cache["timestamp"] = time.time()
            _player_rankings_cache["all_players"] = all_players
    
    try:
        rankings = get_player_rankings_cached(all_players=all_players, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors du scraping des classements: {exc}"
        ) from exc

    if not rankings:
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée de classement trouvée"
        )

    return JSONResponse(content=rankings)


@app.get("/health", summary="Vérification de l'API")
def health_check():
    return {"status": "ok"}

