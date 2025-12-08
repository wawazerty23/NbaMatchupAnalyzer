from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import streamlit as st

TEAM_STATS = []
AVERAGES = {}

def load_team_stats():
    global TEAM_STATS, AVG_2PTS, AVG_3PTS, AVERAGES

    # Charger les stats d'équipe
    driver = webdriver.Chrome()
    driver.get("https://www.nba.com/stats/teams/scoring?dir=A")
    time.sleep(1)
    html_content_team = driver.page_source
    
    # Charger les stats des adversaires
    driver.get("https://www.nba.com/stats/teams/opponent-shots-general?dir=A")
    time.sleep(1)
    html_content_opp = driver.page_source

    # Charger les stats avancées  
    driver.get("https://www.nba.com/stats/teams/advanced?dir=A")
    time.sleep(1)
    html_advanced = driver.page_source
    driver.quit()

    # Parser les deux pages
    soup_team = BeautifulSoup(html_content_team, 'html.parser')
    soup_opp = BeautifulSoup(html_content_opp, 'html.parser')
    soup_adv = BeautifulSoup(html_advanced, 'html.parser')

    # Dictionnaire pour stocker temporairement les stats par équipe
    team_data = {}

    # Traiter les stats d'équipe
    elements_team = soup_team.find_all('tbody')
    for element in elements_team:
        if len(element.find_all('tr')) > 20:
            rows = element.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    team_name = columns[1].text.strip()
                    team_data[team_name] = {
                        'team': team_name,
                        '% 3pts': float(columns[10].text.strip()),
                        '% 2pts': float(columns[8].text.strip())
                    }

    # Traiter les stats des adversaires
    elements_opp = soup_opp.find_all('tbody')
    for element in elements_opp:
        if len(element.find_all('tr')) > 20:
            rows = element.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    team_name = columns[0].text.strip()
                    if team_name in team_data:
                        team_data[team_name].update({
                            'Opponent % 3pts': float(columns[15].text.strip()),
                            'Opponent % 2pts': float(columns[11].text.strip())
                        })

    elements_adv = soup_adv.find_all('tbody')
    for element in elements_adv:
        if len(element.find_all('tr')) > 20:
            rows = element.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    team_name = columns[1].text.strip()
                    if team_name in team_data:
                        team_data[team_name].update({
                            'Reb %': float(columns[14].text.strip()),
                            'Pace': float(columns[18].text.strip()),
                            'OFFRTG': float(columns[6].text.strip()),  # Ajout de l'Offensive Rating
                            'DEFRTG': float(columns[7].text.strip())   # Ajout du Defensive Rating
                        })

    # Convertir le dictionnaire en liste et mettre à jour TEAM_STATS
    TEAM_STATS = list(team_data.values())

    # Calculer les moyennes
    total_2pts = sum(team['% 2pts'] for team in TEAM_STATS)
    total_3pts = sum(team['% 3pts'] for team in TEAM_STATS)
    total_opp_2pts = sum(team['Opponent % 2pts'] for team in TEAM_STATS)
    total_opp_3pts = sum(team['Opponent % 3pts'] for team in TEAM_STATS)
    total_reb = sum(team['Reb %'] for team in TEAM_STATS)
    total_pace = sum(team['Pace'] for team in TEAM_STATS)
    total_offrtg = sum(team['OFFRTG'] for team in TEAM_STATS)
    total_defrtg = sum(team['DEFRTG'] for team in TEAM_STATS)

    # Créer un objet pour stocker toutes les moyennes
    AVERAGES = {
        'team_2pts': total_2pts / len(TEAM_STATS) if TEAM_STATS else 0,
        'team_3pts': total_3pts / len(TEAM_STATS) if TEAM_STATS else 0,
        'opp_2pts': total_opp_2pts / len(TEAM_STATS) if TEAM_STATS else 0,
        'opp_3pts': total_opp_3pts / len(TEAM_STATS) if TEAM_STATS else 0,
        'reb': total_reb / len(TEAM_STATS) if TEAM_STATS else 0,
        'pace': total_pace / len(TEAM_STATS) if TEAM_STATS else 0,
        'offrtg': total_offrtg / len(TEAM_STATS) if TEAM_STATS else 0,  # Moyenne OFFRTG
        'defrtg': total_defrtg / len(TEAM_STATS) if TEAM_STATS else 0   # Moyenne DEFRTG
    }

    print(f"Moyenne équipe % 2pts: {AVERAGES['team_2pts']:.2f}%")
    print(f"Moyenne équipe % 3pts: {AVERAGES['team_3pts']:.2f}%")
    print(f"Moyenne adversaire % 2pts: {AVERAGES['opp_2pts']:.2f}%")
    print(f"Moyenne adversaire % 3pts: {AVERAGES['opp_3pts']:.2f}%")
    print(f"Moyenne Reb %: {AVERAGES['reb']:.2f}%")
    print(f"Moyenne Pace: {AVERAGES['pace']:.2f}")
    print("Toutes les statistiques ont été chargées avec succès.")

def get_team_stats_by_name(team_name):  # Récupérer les stats d'une équipe spécifique
    global TEAM_STATS  # Assurez-vous d'utiliser la variable globale

    # Charger les données si elles ne sont pas encore chargées
    if not TEAM_STATS:
        print("Chargement des statistiques des équipes...")
        load_team_stats()

    team_name = team_name.lower()  # Convertir le nom recherché en minuscules
    for team in TEAM_STATS:
        if team_name in team['team'].lower():  # Vérifier si une partie du nom correspond
            return team
    return None  # Retourne None si l'équipe n'est pas trouvée


def get_averages():  # Récupérer toutes les moyennes
    return AVERAGES

def analyze_matchup(attacking_team, defending_team, shot_type, averages):
    """
    Analyse l'avantage offensif ou défensif entre deux équipes pour un type de tir donné.
    
    Args:
        attacking_team (dict): Statistiques de l'équipe en attaque
        defending_team (dict): Statistiques de l'équipe en défense
        shot_type (str): Type de tir ('2pts' ou '3pts')
        averages (dict): Moyennes de la ligue
    """
    team_avg_key = f'team_{shot_type}'
    opp_avg_key = f'opp_{shot_type}'
    team_stat_key = f'% {shot_type}'
    opp_stat_key = f'Opponent % {shot_type}'

    if attacking_team[team_stat_key] > averages[team_avg_key] + 2:
        if defending_team[opp_stat_key] > averages[opp_avg_key] + 2:
            return st.info(f"🎯 Avantage {attacking_team['team']} sur les tirs à {shot_type}")
        elif defending_team[opp_stat_key] < averages[opp_avg_key] - 2:
            return st.info(f"🛡️ Avantage défensif {defending_team['team']} sur les tirs à {shot_type}")

def display_team_metrics(col, team, averages):
    """
    Fonction helper pour afficher les métriques d'une équipe dans une colonne de manière compacte.
    """
    with col:
        st.write(f"**{team['team']}**")
        
        # Tirs à 2 points
        delta_2pts = team['% 2pts'] - averages['team_2pts']
        st.write(
            f"Tirs à 2pts: {team['% 2pts']}% (Δ: {delta_2pts:+.1f}%)"
        )
        st.write(
            f"   Concédés: {team['Opponent % 2pts']}% "
            f"(Δ: {averages['opp_2pts'] - team['Opponent % 2pts']:+.1f}%)"
        )
        
        # Tirs à 3 points
        delta_3pts = team['% 3pts'] - averages['team_3pts']
        st.write(
            f"Tirs à 3pts: {team['% 3pts']}% (Δ: {delta_3pts:+.1f}%)"
        )
        st.write(
            f"   Concédés: {team['Opponent % 3pts']}% "
            f"(Δ: {averages['opp_3pts'] - team['Opponent % 3pts']:+.1f}%)"
        )
        
        # Pourcentage de rebonds
        delta_reb = team['Reb %'] - averages['reb']
        st.write(
            f"Rebonds (%): {team['Reb %']}% (Δ: {delta_reb:+.1f}%)"
        )
        
        # Rythme de jeu (Pace)
        delta_pace = team['Pace'] - averages['pace']
        st.write(
            f"Pace: {team['Pace']} (Δ: {delta_pace:+.1f})"
        )

        # Offensive Rating (OFFRTG)
        delta_offrtg = team['OFFRTG'] - averages['offrtg']
        st.write(
            f"OFFRTG: {team['OFFRTG']} (Δ: {delta_offrtg:+.1f})"
        )

        # Defensive Rating (DEFRTG)
        delta_defrtg = team['DEFRTG'] - averages['defrtg']
        st.write(
            f"DEFRTG: {team['DEFRTG']} (Δ: {delta_defrtg:+.1f})"
        )

def analyze_team_performance(team1_name, team2_name):
    """
    Analyse et compare les performances de deux équipes par rapport aux moyennes de la ligue.
    """
    team1 = get_team_stats_by_name(team1_name)
    team2 = get_team_stats_by_name(team2_name)
    averages = get_averages()

    if not team1 or not team2:
        if not team1:
            st.error(f"L'équipe {team1_name} n'a pas été trouvée.")
        if not team2:
            st.error(f"L'équipe {team2_name} n'a pas été trouvée.")
        return

    # Création de deux colonnes pour la comparaison
    col1, col2 = st.columns(2)

    # Analyse des matchups
    st.subheader("Analyse des confrontations")
    
    # Analyse team1 vs team2
    analyze_matchup(team1, team2, "2pts", averages)
    analyze_matchup(team1, team2, "3pts", averages)
    
    # Analyse team2 vs team1
    analyze_matchup(team2, team1, "2pts", averages)
    analyze_matchup(team2, team1, "3pts", averages)

    # Analyse des rebonds
    reb_diff = team1['Reb %'] - team2['Reb %']
    if reb_diff > 3:
        st.info(f"🏀 Avantage rebond pour {team1['team']} : +{reb_diff:.1f}% par rapport à {team2['team']}")
    elif reb_diff < -3:
        st.info(f"🏀 Avantage rebond pour {team2['team']} : +{-reb_diff:.1f}% par rapport à {team1['team']}")

    # Analyse du rythme de jeu (Pace)
    pace_diff = team1['Pace'] - team2['Pace']
    if abs(pace_diff) > 3:
        if pace_diff > 0:
            st.info(f"⚡ Différence de rythme marquante : {team1['team']} joue plus vite (+{pace_diff:.1f}) que {team2['team']}")
        else:
            st.info(f"⚡ Différence de rythme marquante : {team2['team']} joue plus vite (+{-pace_diff:.1f}) que {team1['team']}")

    # Affichage des statistiques détaillées dans les colonnes
    display_team_metrics(col1, team1, averages)
    display_team_metrics(col2, team2, averages)

if __name__ == "__main__":
    load_team_stats()
    team_data = get_team_stats_by_name("Utah Jazz")

    print(f"Statistiques pour Utah Jazz:  {team_data}")