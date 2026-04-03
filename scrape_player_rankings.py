#!/usr/bin/env python3
"""
Script pour extraire les données des joueurs depuis basketballmonster.com/playerrankings.aspx
et les retourner en JSON. Inclut l'option pour récupérer tous les joueurs (All Players).
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from typing import List, Dict, Any

def fetch_player_rankings(all_players: bool = True, url: str = "https://basketballmonster.com/playerrankings.aspx") -> List[Dict[str, Any]]:
    """
    Récupère la page des classements de joueurs et extrait les données du tableau.
    
    Args:
        all_players: Si True, active le filtre "All Players" via une requête POST.
                     Si False, récupère seulement les "Top Players" (par défaut).
        url: URL de la page des classements
        
    Returns:
        Liste de dictionnaires, chaque dictionnaire représentant un joueur avec ses attributs.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    session = requests.Session()
    
    try:
        # Première requête GET pour obtenir les champs cachés
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extraire les champs cachés nécessaires pour POST
    hidden_inputs = soup.find_all('input', type='hidden')
    post_data = {}
    for inp in hidden_inputs:
        name = inp.get('name')
        value = inp.get('value', '')
        if name:
            post_data[name] = value
    
    # Si on veut tous les joueurs, ajouter le paramètre pour le filtre
    if all_players:
        post_data['PlayerFilterControl'] = 'AllPlayers'
        post_data['__EVENTTARGET'] = 'PlayerFilterControl'
        post_data['__EVENTARGUMENT'] = ''
        
        # Envoyer la requête POST avec les mêmes champs cachés
        try:
            response = session.post(url, headers=headers, data=post_data, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête POST: {e}", file=sys.stderr)
            # Fallback sur GET
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trouver le tableau des classements - plusieurs classes possibles
    table = None
    # Essayer avec la classe exacte
    table = soup.find('table', {'class': 'table-bordered table-hover table-sm base-td-small datatable ml-0'})
    if not table:
        # Essayer avec une recherche partielle
        table = soup.find('table', class_=lambda c: c and 'table' in c and 'datatable' in c)
    if not table:
        print("Tableau des classements non trouvé.", file=sys.stderr)
        return []
    
    # Extraire les en-têtes
    thead = table.find('thead')
    if not thead:
        print("En-têtes du tableau non trouvés.", file=sys.stderr)
        return []
    
    header_cells = thead.find_all('th')
    headers = []
    for th in header_cells:
        # Nettoyer le texte de l'en-tête
        text = th.get_text(strip=True)
        # Si c'est un lien, on prend le texte du lien
        a = th.find('a')
        if a and a.get_text(strip=True):
            text = a.get_text(strip=True)
        headers.append(text)
    
    # Noms de colonnes normalisés
    column_names = [
        'round', 'rank', 'value', 'name', 'team', 'pos', 'inj', 'games',
        'minutes_per_game', 'points_per_game', 'threes_per_game', 'rebounds_per_game',
        'assists_per_game', 'steals_per_game', 'blocks_per_game', 'fg_percent',
        'fga_per_game', 'ft_percent', 'fta_per_game', 'turnovers_per_game',
        'usage', 'points_value', 'threes_value', 'rebounds_value', 'assists_value',
        'steals_value', 'blocks_value', 'fg_percent_value', 'ft_percent_value',
        'turnovers_value'
    ]
    
    # S'assurer que le nombre de colonnes correspond
    if len(headers) != len(column_names):
        print(f"Nombre d'en-têtes ({len(headers)}) ne correspond pas aux colonnes attendues ({len(column_names)}).", file=sys.stderr)
        # On utilise les en-têtes bruts si la taille diffère
        column_names = [f"col{i}" for i in range(len(headers))]
    
    # Extraire les lignes de données
    # Certains tableaux n'ont pas de tbody, les tr sont directement dans le tableau
    rows = table.find_all('tr')
    # Exclure les lignes d'en-tête si elles sont présentes
    rows = [row for row in rows if row.find('th') is None]
    players = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) != len(column_names):
            # Certaines lignes peuvent avoir un nombre différent de cellules (ex: lignes vides)
            continue
        
        player_data = {}
        name = None
        team = None
        
        for i, cell in enumerate(cells):
            col_name = column_names[i]
            cell_text = cell.get_text(strip=True)
            
            # Convertir les valeurs numériques quand c'est possible
            if cell_text == '' or cell_text == '&nbsp;' or cell_text == '\xa0':
                cell_text = None
            else:
                # Essayer de convertir en nombre
                try:
                    # Pour les pourcentages, enlever le point de début
                    if col_name in ['fg_percent', 'ft_percent'] and cell_text.startswith('.'):
                        cell_text = '0' + cell_text
                    # Convertir en float si possible
                    if '.' in cell_text:
                        cell_text = float(cell_text)
                    else:
                        cell_text = int(cell_text)
                except ValueError:
                    # Garder comme chaîne
                    pass
            
            # Extraire name et team pour les mettre au niveau supérieur
            if col_name == 'name':
                name = cell_text
            elif col_name == 'team':
                team = cell_text
            else:
                player_data[col_name] = cell_text
        
        # Extraire l'ID du joueur depuis le lien
        link = cells[3].find('a')  # La quatrième cellule contient le nom avec lien
        if link:
            href = link.get('href', '')
            if 'i=' in href:
                player_id = href.split('i=')[1].split('&')[0]
                player_data['player_id'] = int(player_id)
            else:
                player_data['player_id'] = None
        else:
            player_data['player_id'] = None
        
        # Créer l'objet restructuré
        player_obj = {
            'name': name,
            'team': team,
            'data': player_data
        }
        
        players.append(player_obj)
    
    return players

def main():
    """Fonction principale."""
    import argparse
    parser = argparse.ArgumentParser(description='Extract player rankings from Basketball Monster.')
    parser.add_argument('--top-only', action='store_true', help='Fetch only top players (default: all players)')
    parser.add_argument('--output', default='player_rankings.json', help='Output JSON file path')
    args = parser.parse_args()
    
    all_players = not args.top_only
    filter_type = "All Players" if all_players else "Top Players"
    print(f"Extraction des données des joueurs ({filter_type}) depuis basketballmonster.com...")
    
    players = fetch_player_rankings(all_players=all_players)
    
    if not players:
        print("Aucune donnée extraite.", file=sys.stderr)
        sys.exit(1)
    
    # Afficher le nombre de joueurs extraits
    print(f"{len(players)} joueurs extraits.")
    
    return players

if __name__ == "__main__":
    main()