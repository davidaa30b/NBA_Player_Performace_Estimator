import time
import requests
from bs4 import BeautifulSoup,Comment
from performance_estimator.models import Team, TeamGameLogGeneralStats,TeamGameLogAdvancedStats
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR, ADVANCED_STATS, GENERAL_STATS
from performance_estimator.utils.exceptions import PageCouldNotBeRetrievedError, TableNotFoundError
from performance_estimator.utils.prepare_for_save_data import retrive_data_for_columns_from_table, sanitize_data


def get_team_table_logs(team_name, log_type):
    if log_type == GENERAL_STATS:
        team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}/gamelog/"
        table_type =" tgl_basic"
    elif log_type == ADVANCED_STATS:
        team_url =  f"{SITE_LINK}/teams/{team_name}/{YEAR}/gamelog-advanced"
        table_type = "tgl_advanced"
    time.sleep(5) 
    response = requests.get(team_url,headers= BROWSER_HEADERS)
    if response.status_code != 200:
        raise PageCouldNotBeRetrievedError(page_type=f'team page for {team_name}',status_code=response.status_code)
    team_log_soup = BeautifulSoup(response.text, 'html.parser')
    log_table = team_log_soup.find('table', {'id': table_type})

    if not log_table:
        raise TableNotFoundError('Team logs')
    return log_table

def get_team_game_log_columns(log_table,log_type):
    header_row = log_table.find('thead').find_all('th')
    if log_type == GENERAL_STATS:
        columns = [header.text.strip() for header in header_row][6:]
        columns[3] = 'Location'
        columns[4] = 'Opponent Name'

    elif log_type == ADVANCED_STATS:
        columns = [header.text.strip() for header in header_row][8:]
        columns[3] = 'Location'
        columns[4] = 'Opponent Name'
        columns[19] = 'offensive eFG%'
        columns[20] = 'offensive TOV%'
        columns[21] = 'offensive ORB%'
        columns[22] = 'offensive FT/FGA'

        columns[24] = 'defensive eFG%'
        columns[25] = 'defensive TOV%'
        columns[26] = 'defensive DRB%'
        columns[27] = 'defensive FT/FGA'
    return columns

def fetch_game_data_for_team(columns,row,index):
    cols = row.find_all('td')
    game_data = None
    try:
        if len(cols) > 0:
            game_data = retrive_data_for_columns_from_table(columns,cols)
            print(game_data)
            game_data['Location'] =  game_data['Location'] != '@'
            rank = row.find('th')
            game_data[columns[0]] = rank.text.strip()  
            game_data[columns[1]] = index + 1

    except :
        game_data = None    
    return game_data

def save_game_data_team(log_type, game_data, team:Team, columns):
    stats_model = {
        GENERAL_STATS: TeamGameLogGeneralStats,
        ADVANCED_STATS: TeamGameLogAdvancedStats
    }.get(log_type)

    if not stats_model:
        raise ValueError("Invalid log type provided")

    properties = stats_model.get_properties()
    cleaned_fields = [field for field in columns if field != '']
    properties = properties[1:len(properties)-1]

    game_stats_data = {properties[index]: game_data[cleaned_fields[index]] for index in range(len(cleaned_fields))}
    
    game_stats_data.update({
        "team": team,
        "season": YEAR
    })
    int_fields = set(stats_model.get_int_fields()) 
    float_fields = set(stats_model.get_float_fields()) 
    sanitize_data(game_stats_data,int_fields,float_fields)
    
    game_stats = stats_model(**game_stats_data)
    game_stats.save()
    return game_stats

def get_team_games_log(team: Team,log_type=GENERAL_STATS):
    team_name: str = team.abbreviation
    print(team_name,log_type,"team games fetch")

    log_table = get_team_table_logs(team_name,log_type)
    columns = get_team_game_log_columns(log_table,log_type)

    rows = log_table.find('tbody').find_all('tr')
    for index, row in enumerate(rows):
        if 'thead' in row.get('class', []):
            continue
        game_data =  fetch_game_data_for_team(columns,row,index)
        if game_data:  
            if log_type == ADVANCED_STATS :
                existing_game_stats = TeamGameLogAdvancedStats.objects.filter(team=team, date=game_data['Date']).first()
            else:
                existing_game_stats = TeamGameLogGeneralStats.objects.filter(team=team, date=game_data['Date']).first()
       
        if game_data and not existing_game_stats:
            save_game_data_team(log_type,game_data,team,columns)
        else:
            print(f"No games log data found for {team}")


