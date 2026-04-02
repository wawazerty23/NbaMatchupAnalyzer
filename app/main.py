from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from players_status import get_injured_players


app = FastAPI(
    title="NBA Injuries API",
    description="Expose la liste des joueurs blessés via FastAPI",
    version="1.0.0",
)


@app.get("/player_status", summary="Liste des joueurs blessés")
def read_player_status():
    try:
        injured_players = get_injured_players()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur de récupération: {exc}") from exc

    # Retour JSON brut pour garder la structure existante
    return JSONResponse(content=injured_players)


@app.get("/health", summary="Vérification de l'API")
def health_check():
    return {"status": "ok"}

