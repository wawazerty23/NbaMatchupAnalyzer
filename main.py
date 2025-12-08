from nba_api.stats.endpoints import CommonTeamRoster, commonplayerinfo, playerdashboardbyyearoveryear
from nba_api.stats.static import players, teams
import streamlit as st
from datetime import datetime
import time

st.title("NBA Pool Champion's Tool (Warren)")

def calculate_age(birth_date_str):
    try:
        # Parse the input string to a datetime object
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # Handle the case where the format does not match
        raise ValueError("Incorrect date format, should be YYYY-MM-DDTHH:MM:SS")

    # Get today's date
    today = datetime.today()
    
    # Calculate age
    age = today.year - birth_date.year
    
    # Adjust if the birth date hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
        
    return age

@st.cache_data
def get_team_roster(team_name):
    team = teams.find_teams_by_full_name(team_name)
    roster = CommonTeamRoster(team[0]['id']).get_normalized_dict()

    players_with_fantasy_pts = []
    for player in roster['CommonTeamRoster']:
        player_seasons = get_season_list(player['PLAYER_ID'])
        if player_seasons:
            players_with_fantasy_pts.append({
                'name': player['PLAYER'],
                'fantasy_pts': player_seasons[0]['NBA_FANTASY_PTS'],
                'gp': player_seasons[0]['GP']
            })

    return players_with_fantasy_pts


def display_team_roster(team_name):
    players_with_fantasy_pts = get_team_roster(team_name)

    sorted_players = sorted(players_with_fantasy_pts, key=lambda x: x['fantasy_pts'], reverse=True)
    

    st.write("Best team mates:")
    str = ""
    with st.container(border=True):
        for player in sorted_players[:6]:
            fpg = round(float(player['fantasy_pts']) / float(player['gp']), 1) if int(player['gp']) > 0 else 0
            str = str + f"{player['name']} {player['fantasy_pts']} pts {fpg} fpg\n"
        st.text(str)


@st.cache_data
def get_player_id(player_full_name):
    active_players = players.get_active_players()
    names = [player['full_name'] for player in active_players]
        
    if player_full_name:
        # Find the index of the selected player
        index = names.index(player_full_name)
        return active_players[index]['id']
    else:
        return None
    
@st.cache_data
def get_season_list(player_id):
    dashboard = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id)
    time.sleep(0.1)
    season_list = dashboard.get_normalized_dict()['ByYearPlayerDashboard']

    new_season_list = []
    season_added = []
    for index, season in enumerate(season_list):
        if index + 1 < len(season_list):
            if season_list[index + 1]["GROUP_VALUE"] == season_list[index]["GROUP_VALUE"]:
                if season_list[index]['TEAM_ABBREVIATION'] == "TOT":
                    new_season_list.append(season_list[index])
                    season_added.append(season_list[index]["GROUP_VALUE"])

          
        if season_list[index]["GROUP_VALUE"] not in season_added:
            new_season_list.append(season_list[index])
            season_added.append(season_list[index]["GROUP_VALUE"])

    return new_season_list

def display_player_dashboard_by_year(player_id):
    
    season_list = get_season_list(player_id=player_id)
    #st.text(season_list)

    if season_list:
        current_s = season_list[0]
        last_s = season_list[1] if len(season_list) > 1 else season_list[0]

        fantasy_diff = int(current_s['NBA_FANTASY_PTS']) - int(last_s['NBA_FANTASY_PTS'])
        gp_diff = int(current_s['GP']) - int(last_s['GP'])
        
        # Calculate fantasy points per game
        current_fpg = round(float(current_s['NBA_FANTASY_PTS']) / float(current_s['GP']), 1) if int(current_s['GP']) > 0 else 0
        last_fpg = round(float(last_s['NBA_FANTASY_PTS']) / float(last_s['GP']), 1) if int(last_s['GP']) > 0 else 0
        fpg_diff = round(current_fpg - last_fpg, 1)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Fantasy points", current_s['NBA_FANTASY_PTS'], fantasy_diff)
        col2.metric("Game played", current_s['GP'], gp_diff)
        col3.metric("Fantasy pts/game", current_fpg, fpg_diff)

    else:
        st.text("No stats available")


@st.cache_data
def get_player_commom_info(player_id):
    info = commonplayerinfo.CommonPlayerInfo(player_id)
    dict_info = info.get_normalized_dict()
    commonInfo = dict_info['CommonPlayerInfo'][0]
    return commonInfo

def display_player_common_info(player_id):
    commonInfo = get_player_commom_info(player_id)

    st.text(commonInfo['DISPLAY_FIRST_LAST'])
    st.text("Age: {}".format(calculate_age(commonInfo['BIRTHDATE'])))
    st.text("Season experience: {} years".format(commonInfo['SEASON_EXP']))
    st.text("Position: {}".format(commonInfo['POSITION']))
    st.text("Team: {}".format(commonInfo['TEAM_NAME']))
    #stats = dict_info['PlayerHeadlineStats'][0]
    #st.text("PIE: {}".format(stats['PIE']))

    return commonInfo['TEAM_NAME']

    
active_layers = players.get_active_players()
names = [player['full_name'] for player in active_layers]

player_number = st.selectbox("How many players to analyse ?", [1,2,3])
columns = st.columns(player_number)

for i, col in enumerate(columns):
    with col:
        selected_name = st.selectbox(f"Select player {i}", names)
        player_id = get_player_id(selected_name)
        team_name = display_player_common_info(player_id)
        display_player_dashboard_by_year(player_id)
        display_team_roster(team_name)
