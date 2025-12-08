import requests
from bs4 import BeautifulSoup
import time
from functools import lru_cache

def get_bpi(url="https://www.espn.com/nba/bpi"):
    # Définir les en-têtes pour la requête
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    @lru_cache(maxsize=1)
    def cached_get_bpi():
        current_time = time.time()
        if not hasattr(cached_get_bpi, "last_updated") or current_time - cached_get_bpi.last_updated > 3600:
            cached_get_bpi.last_updated = current_time
            response = requests.get(url, headers=headers)
            cached_get_bpi.cached_response = response.content
        return cached_get_bpi.cached_response

    html_content = cached_get_bpi()
    soup = BeautifulSoup(html_content, 'html.parser')

    team_names = []

    for img_tag in soup.find_all('img', class_='Image Logo Logo__sm'):
        if 'alt' in img_tag.attrs:
            team_names.append(img_tag['alt'])

    # Trouver toutes les lignes de la table contenant les données du BPI dans le body <tbody class="Table__TBODY">
    div = soup.find('div', class_='Table__ScrollerWrapper relative overflow-hidden')
    rows = div.find_all('tr', class_='Table__TR Table__TR--sm Table__even')

    # Extraire les données des cellules et les stocker dans un tableau de listes
    bpi_stats = []
    for row in rows:
        cells = row.find_all('td', class_='Table__TD')
        ligne = [cell.div.text for cell in cells]
        bpi_stats.append(ligne)

    bpi_dict = {team_names[i]: bpi_stats[i] for i in range(len(team_names))}
    return bpi_dict




