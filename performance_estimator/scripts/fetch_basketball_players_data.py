import time
import requests
from bs4 import BeautifulSoup
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR, ADVANCED_STATS, GENERAL_STATS
from performance_estimator.models import Player, PlayerSeason, Team, GameLogPlayerAdvancedStats, GameLogPlayerGeneralStats
from performance_estimator.utils.exceptions import TableNotFoundError
from performance_estimator.utils.prepare_for_save_data import retrive_data_for_columns_from_table, sanitize_data


def fetch_roster_table(team: Team):
    team_name: str = team.abbreviation
    team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}.html"
    time.sleep(2) 
    response = requests.get(team_url,headers= BROWSER_HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the team page for {team_name}. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    roster_table = soup.find('table', {'id': 'roster'})
    if roster_table is None:
        raise TableNotFoundError("Roster")
    return roster_table

def get_players_game_logs_links(roster_table, log_type):
    if not roster_table:
        raise TableNotFoundError("Roster")
    player_links = []
    for row in roster_table.find_all('tr')[1:]:  
        player_name_column = row.find('td', {'data-stat': 'player'})
        if player_name_column:
            player_name = player_name_column.find('a').text.strip()
            player_link = player_name_column.find('a')['href']
            player_links.append((SITE_LINK + player_link, player_name))
    games_log_links = []
    for player_url, player_name in player_links:
        time.sleep(2) 
        base_url = player_url.replace('.html', '')
        if log_type == GENERAL_STATS:
            transformed_url = f"{base_url}/gamelog/{YEAR}"
        elif log_type == ADVANCED_STATS:
            transformed_url = f"{base_url}/gamelog-advanced/{YEAR}"
        games_log_links.append((transformed_url ,player_name))
    return games_log_links

def fetch_player_game_log(team,player_games_log_url,player_name,table_type):
    created_player = Player.objects.filter(name=player_name).first()

    if not created_player:
        created_player = Player(name=player_name)
        created_player.save()

    player_season = PlayerSeason.objects.filter(player=created_player, team=team, year=YEAR).first()

    if not player_season:
        player_season = PlayerSeason(player=created_player, team=team, year=YEAR)
        player_season.save()

    time.sleep(2) 
    games_log_response = requests.get(player_games_log_url,headers= BROWSER_HEADERS)
    print(player_season)
    if games_log_response.status_code != 200:
        return None
    
    games_log_soup =  BeautifulSoup(games_log_response.text, 'html.parser')
    game_log_table = games_log_soup.find('table', {'id': table_type})
    if game_log_table is None:
        raise TableNotFoundError("Game log for ${player_name}")
 
    return game_log_table,games_log_response,player_season

def fetch_game_data_for_player(columns,row,index):
    cols = row.find_all('td')
    game_data = None

    try:
        if len(cols) > 0:
            game_data = retrive_data_for_columns_from_table(columns,cols)
            game_data['Location'] =  game_data['Location'] != '@' 
            rank = row.find('th')
            game_data[columns[0]] = rank.text.strip()  
            game_data[columns[1]] = index + 1
    except:
        game_data = None
    
    return game_data
        
def save_game_data_player(log_type, game_data, player_season, columns):
    stats_model = {
        GENERAL_STATS: GameLogPlayerGeneralStats,
        ADVANCED_STATS: GameLogPlayerAdvancedStats
    }.get(log_type)

    if not stats_model:
        raise ValueError("Invalid log type provided")

    properties = stats_model.get_properties()[1:-1]
    game_stats_data = {properties[index]: game_data[columns[index]] for index in range(len(columns))}
    
    game_stats_data.update({
        "player": player_season,
        "season": YEAR
    })
    int_fields = set(stats_model.get_int_fields()) 
    float_fields = set(stats_model.get_float_fields()) 
    sanitize_data(game_stats_data,int_fields,float_fields)
    
    game_stats = stats_model(**game_stats_data)
    game_stats.save()
    return game_stats



def get_player_games_log(team: Team,log_type=GENERAL_STATS):
    
    roster_table = fetch_roster_table(team)

    if log_type == GENERAL_STATS:
        table_type = "pgl_basic"
    elif log_type == ADVANCED_STATS:
        table_type = "pgl_advanced"

    games_log_links = get_players_game_logs_links(roster_table, log_type)
        
    for player_games_log_url, player_name in games_log_links:
        log_table, games_log_response,player_season = fetch_player_game_log(team,player_games_log_url,player_name,table_type)
        if games_log_response.status_code != 200:
            print(f"Failed to retrieve the game log page for {player_name}. Status code: {games_log_response.status_code}")
            continue
        
        if log_table:
            header_row = log_table.find('thead').find_all('th')
            columns = [header.text.strip() for header in header_row]
            columns[5] = "Location"
            columns[7] = "Margin"
            rows = log_table.find('tbody').find_all('tr')
            for index, row in enumerate(rows):
                game_data = fetch_game_data_for_player(columns,row,index)
                if game_data:        
                    if log_type == ADVANCED_STATS :
                        existing_game_stats = GameLogPlayerAdvancedStats.objects.filter(player=player_season, date=game_data['Date']).first()
                    else :
                        existing_game_stats = GameLogPlayerGeneralStats.objects.filter(player=player_season, date=game_data['Date']).first()

                        
                if game_data and not existing_game_stats:
                    save_game_data_player(log_type,game_data,player_season,columns)
        else:
            print(f"No games log data found for {player_name}")





