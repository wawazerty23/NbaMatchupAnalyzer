import requests
from bs4 import BeautifulSoup

# Variable pour stocker le résultat en cache
_cached_schedule = None

def get_schedule(url="https://www.espn.com/nba/schedule"):
    global _cached_schedule

    # Si le résultat est déjà calculé, le retourner directement
    if _cached_schedule is not None:
        return _cached_schedule

    # Définir les en-têtes pour la requête
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trouver toutes les sections de dates et leurs matchs associés
    matches_by_date = {}
    for date_section in soup.select('.Table__Title'):
        date = date_section.text.strip()
        matches_by_date[date] = []

        # Trouver les matchs associés à cette date
        table_body = date_section.find_next('tbody')
        if table_body:
            rows = table_body.select('.Table__TR--hasNote.Table__TR, .Table__TR.Table__TR--sm')
            matches_by_date[date] = []

            for row in rows:
                away_team = row.select_one('.Table__Team.away a:last-child')
                home_team = row.select_one('.Table__Team:not(.away) a:last-child')
                odds_element = row.select_one('.odds__col.Table__TD [data-testid="OddsFragmentLine"]')

                if away_team and home_team:
                    match = f"{away_team.text.strip()}@{home_team.text.strip()}"
                    # Extraire uniquement la partie des cotes après "Line: "
                    odds = odds_element.text.strip().replace("Line: ", "") if odds_element else "N/A"
                    matches_by_date[date].append(f"{match} ({odds})")

    # Stocker le résultat dans le cache
    _cached_schedule = matches_by_date

    # Afficher les résultats
    for date, matches in matches_by_date.items():
        print(f"Date: {date}")
        for match in matches:
            print(f"  Match: {match}")

    return matches_by_date
