from nba_api.stats.endpoints import TeamGameLogs, CumeStatsTeamGames, CumeStatsTeam
from nba_api.stats.static import players, teams
from players_status import get_injured_players
from team_pbi import get_bpi
from schedule import get_schedule
from advancedStats import analyze_team_performance
import streamlit as st
from annotated_text import annotated_text
from datetime import datetime
import re

st.set_page_config(layout="wide")


def get_correct_team_name(team):
    team = team.strip()
    if team == "LA":
        return "Clippers"
    elif team == "Los Angeles":
        return "Lakers"
    else:
        return team

def calculer_pourcentage_victoire(rowSet):
    total_matchs = len(rowSet)
    if total_matchs == 0:
        return 0

    victoires = sum(1 for match in rowSet if match[7] == 'W')
    
    pourcentage_victoire = (victoires / total_matchs) * 100
    return pourcentage_victoire

def display_team_info(team):
    gamelogs = TeamGameLogs(
    last_n_games_nullable=10,
    team_id_nullable=team['id'],
    season_nullable="2025-26"
    ).get_dict()
    rowSet = gamelogs['resultSets'][0]['rowSet']
    #st.write(rowSet)
    
    bpi_stats = get_bpi()
    container_win = st.container(border=True)
    container_inj = st.container(border=True)

    with container_win:
        st.write(team['full_name'])
        team_name_bpi = "LA Clippers" if team['full_name'] == "Los Angeles Clippers" else team['full_name']
        st.caption(f"W-L: {bpi_stats[team_name_bpi][0]}")
        st.caption(f"BPI rank: {bpi_stats[team_name_bpi][2]}")
        win_pct_past = calculer_pourcentage_victoire(rowSet[5:10])
        win_pct = calculer_pourcentage_victoire(rowSet[0:5])
        win_pct_diff = win_pct - win_pct_past

        st.metric("Win % last 5 games", f"{win_pct}%", win_pct_diff)
        for row in rowSet[0:5]:
            date_object = datetime.strptime(row[5].replace("T00:00:00",""), "%Y-%m-%d")
            formatted_date = date_object.strftime("%b %d")
            score_diff = row[29]
            if row[7] == 'W':
                if score_diff >= 10:
                    green_code = green_code_good
                else:
                    green_code = green_code_medium
                annotated_text((f"{row[6]}", f"+{score_diff} - {formatted_date}", green_code))
            else:
                if score_diff <= -10:
                    red_code = red_code_bad
                else:
                    red_code = red_code_medium
                annotated_text((f"{row[6]}", f"{score_diff} - {formatted_date}", red_code))
            #st.write(f"{formatted_date} - {row[6]} : {row[7]}")

    with container_inj:
        team_key = team['full_name'].split()[-1]
        players = injured_players.get(team_key, None)
        
        if players:
            st.write("Joueurs blessés:")
            for player in players:
                if player['status'] == "Out":
                    color = red_code_medium
                else:
                    color = yellow_code
                annotated_text(
                    (f"{player['name']}", f"{player['status']}", color)
                )
        else:
            st.write("Aucun joueur blessé.")

     
injured_players = get_injured_players()
matches_by_date = get_schedule()
current_teams = teams.get_teams()



team_names = [team['full_name'] for team in current_teams ]

red_code_bad = "#ff6b6b"  # Softer red for very bad
red_code_medium = "#ffa3a3"  # Softer medium red
green_code_good = "#6bff6b"  # Softer green for very good
green_code_medium = "#a3ffa3"  # Softer medium green
yellow_code = "#fea"

col_matchs, col_stats, col_advanced = st.columns([1, 3, 3])
with col_matchs:
    selected_date = st.radio("Choisissez une date:", matches_by_date.keys())
    selected_match = st.radio("Choisissez un match:", matches_by_date[selected_date])

with col_stats:
    if selected_match:
        pattern = r"([A-Za-z ]+)@([A-Za-z ]+)"
        match = re.search(pattern, selected_match)

        if match:
            team_1_name = get_correct_team_name(match.group(1))
            team_2_name = get_correct_team_name(match.group(2))

            col1, col2 = st.columns(2)
            with col1:
                team_1_results = teams.find_teams_by_full_name(team_1_name)
                if not team_1_results:
                    st.error(f"Aucune équipe trouvée pour le nom : {team_1_name}")
                else:
                    team_1 = team_1_results[0]
                    display_team_info(team_1)

            with col2:
                team_2_results = teams.find_teams_by_full_name(team_2_name)
                if not team_2_results:
                    st.error(f"Aucune équipe trouvée pour le nom : {team_2_name}")
                else:
                    team_2 = team_2_results[0]
                    display_team_info(team_2)
        else:
            st.error("Impossible de trouver les équipes dans le match sélectionné.")

#with col_advanced:

#    analyze_team_performance(team_1_name, team_2_name)