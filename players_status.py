import requests
from bs4 import BeautifulSoup


def get_injured_players(url="https://www.espn.com/nba/injuries"):

    # Définir les en-têtes pour la requête
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Envoyer une requête GET pour récupérer le contenu de la page avec les en-têtes définis
    response = requests.get(url, headers=headers)
    html_content = response.content

    # Utiliser BeautifulSoup pour analyser le contenu HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trouver toutes les sections d'équipes
    teams_sections = soup.find_all('div', class_='ResponsiveTable Table__league-injuries')

    # Initialiser un dictionnaire pour stocker les informations des équipes et leurs joueurs blessés
    teams_info = {}

    # Parcourir chaque section d'équipe
    for section in teams_sections:
        team_name = section.find('span', class_='injuries__teamName').get_text(strip=True)
        team_name = team_name.split()[-1]

        # Trouver la table des blessures dans cette section
        table = section.find('table', class_='Table')

        # Initialiser une liste pour les joueurs blessés de cette équipe
        players_list = []

        # Parcourir chaque ligne du tableau (chaque joueur)
        for row in table.find('tbody').find_all('tr'):
            player_name = row.find('td', class_='col-name').get_text(strip=True)
            status = row.find('td', class_='col-stat').get_text(strip=True)
            return_date = row.find('td', class_='col-date').get_text(strip=True)

            players_list.append({
                'name': player_name,
                'status': status,
                'return_date': return_date
            })

        # Ajouter la liste des joueurs blessés au dictionnaire avec le nom de l'équipe comme clé
        teams_info[team_name] = players_list

    # Stocker le résultat dans le cache
    _cached_injured_players = teams_info
    return teams_info

if __name__ == "__main__":
    results = get_injured_players()
    print(results)
