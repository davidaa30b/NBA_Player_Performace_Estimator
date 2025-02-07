import time
import requests
from bs4 import BeautifulSoup,Comment
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR, ADVANCED_STATS, GENERAL_STATS
from performance_estimator.models import Player, PlayerSeason, Team, GameLogPlayerAdvancedStats, GameLogPlayerGeneralStats


team_stats = ['injuries','team_and_opponent','team_misc',
              'per_game_stats','per_poss','advanced',
              'adj_shooting','shooting','pbp_stats']

def sanitize_data(data_dict):
    int_fields = set(GameLogPlayerAdvancedStats.get_int_fields()) | set(GameLogPlayerGeneralStats.get_int_fields())
    float_fields = set(GameLogPlayerAdvancedStats.get_float_fields()) | set(GameLogPlayerGeneralStats.get_float_fields())

    for key, value in data_dict.items():
        if key in int_fields and value == '':  
            data_dict[key] = 0
        elif key in float_fields and value == '':  
            data_dict[key] = 0.0
    return data_dict


def scrape_team_roster_stats(team_abbr,stats_type='per_game_stats'):
    url = f'{SITE_LINK}/teams/{team_abbr}/{YEAR}.html'
    response = requests.get(url,headers= BROWSER_HEADERS)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        stats_table = soup.find('table', {'id': stats_type})
        if not stats_table:
                comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    if stats_type in comment:
                        comment_soup = BeautifulSoup(comment, 'html.parser')
                        stats_table = comment_soup.find('table', {'id': stats_type})
                        if stats_table:
                            break
        if stats_table:
            headers = [th.text.strip() for th in stats_table.find_all('th')]
            rows = stats_table.find_all('tr')

            team_stats = []
            for row in rows:
                rk = row.find('th').text.strip()
                columns = row.find_all('td')
               
                if columns:
                    player_stats = {
                    headers[0]: rk 
                    }
                    for i in range(len(columns)):
                        player_stats[headers[i+1]] = columns[i].text.strip() 
                    team_stats.append(player_stats)

            return team_stats
        
        else:
            print(f"No stats table {stats_type} found for team {team_abbr}!")
            return None
    else:
        print(f"Failed to retrieve data for team {team_abbr}. Status code: {response.status_code}")
        return None

def get_player_games_log(team: Team,log_type=GENERAL_STATS):
    team_name: str = team.abbreviation
    print(team_name,log_type,"players games fetch")
    if log_type == GENERAL_STATS:
        table_type = "pgl_basic"
    elif log_type == ADVANCED_STATS:
        table_type = "pgl_advanced"

    team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}.html"
    time.sleep(2) 
    response = requests.get(team_url,headers= BROWSER_HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the team page for {team_name}. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    roster_table = soup.find('table', {'id': 'roster'})
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
        # print("player_url: ",player_url)
        base_url = player_url.replace('.html', '/')
        if log_type == GENERAL_STATS:
            transformed_url = f"{base_url}/gamelog/{YEAR}"
        elif log_type == ADVANCED_STATS:
            transformed_url = f"{base_url}/gamelog-advanced/{YEAR}"

        games_log_links.append((transformed_url ,player_name))
        
        
    for player_games_log_url, player_name in games_log_links:
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
            print(f"Failed to retrieve the game log page for {player_name}. Status code: {games_log_response.status_code}")
            continue
        
        games_log_soup = BeautifulSoup(games_log_response.text, 'html.parser')
        log_table = games_log_soup.find('table', {'id': table_type})
        
        if log_table:
            header_row = log_table.find('thead').find_all('th')
            columns = [header.text.strip() for header in header_row]
            columns[5] = "Location"
            columns[7] = "Margin"
            rows = log_table.find('tbody').find_all('tr')
            for index, row in enumerate(rows):
                if 'thead' in row.get('class', []):
                    continue
                cols = row.find_all('td')
                if len(cols) > 0:
                    try:
                        game_data = {
                            columns[i]: (int(cols[i-1].text.strip()) if cols[i-1].text.strip().isdigit() else
                                        (float(cols[i-1].text.strip()) if '.' in cols[i-1].text.strip() else
                                        cols[i-1].text.strip()))
                            for i in range(2, len(columns))
                        }
                        game_data['Location'] =  game_data['Location'] != '@' #True if Home

                    except :
                        game_data = None

                if game_data is not None:        
                    if log_type == ADVANCED_STATS :
                        existing_game_stats = GameLogPlayerAdvancedStats.objects.filter(player=player_season, date=game_data['Date']).first()
                    else :
                        existing_game_stats = GameLogPlayerGeneralStats.objects.filter(player=player_season, date=game_data['Date']).first()

                        
                if game_data and not existing_game_stats:        
                    rank = row.find('th')
                    if rank:
                        game_data[columns[0]] = rank.text.strip()  
                        game_data[columns[1]] = index + 1
                    
                    if log_type == GENERAL_STATS :
                        properties = GameLogPlayerGeneralStats.get_properties()
                        properties = properties[1:len(properties)-1]
                        game_stats_data = {properties[index]: game_data[columns[index]] for index in range(len(columns))}
                        game_stats_data["player"] = player_season
                        game_stats_data["season"] = YEAR
                        sanitize_data(game_stats_data)
                        game_stats = GameLogPlayerGeneralStats(
                            **game_stats_data
                        )
                    elif log_type == ADVANCED_STATS:
                        properties = GameLogPlayerAdvancedStats.get_properties()
                        properties = properties[1:len(properties)-1]
                        game_stats_data = {properties[index]: game_data[columns[index]] for index in range(len(columns))}
                        game_stats_data["player"] = player_season
                        game_stats_data["season"] = YEAR

                        sanitize_data(game_stats_data)
                        game_stats = GameLogPlayerAdvancedStats(
                           **game_stats_data
                        )            
                    game_stats.save()
        else:
            print(f"No games log data found for {player_name}")


