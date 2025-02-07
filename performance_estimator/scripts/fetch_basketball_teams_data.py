import time
import requests
from bs4 import BeautifulSoup,Comment
from performance_estimator.models import Team, TeamGameLogGeneralStats,TeamGameLogAdvancedStats
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR, ADVANCED_STATS, GENERAL_STATS

def sanitize_data(data_dict):
    int_fields = set(TeamGameLogAdvancedStats.get_int_fields()) | set(TeamGameLogAdvancedStats.get_int_fields())
    float_fields = set(TeamGameLogGeneralStats.get_float_fields()) | set(TeamGameLogGeneralStats.get_float_fields())

    for key, value in data_dict.items():
        if key in int_fields and value == '':  
            data_dict[key] = 0
        elif key in float_fields and value == '':  
            data_dict[key] = 0.0
    return data_dict


def get_team_games_log(team: Team,log_type=GENERAL_STATS):
    team_name: str = team.abbreviation
    print(team_name,log_type,"team games fetch")

    if log_type == GENERAL_STATS:
        table_type = "tgl_basic"
        team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}/gamelog/"
    elif log_type == ADVANCED_STATS:
        table_type = "tgl_advanced"
        team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}/gamelog-advanced"

    time.sleep(5) 
    response = requests.get(team_url,headers= BROWSER_HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the team page for {team_name}. Status code: {response.status_code}")
        return
    
    
    team_log_soup = BeautifulSoup(response.text, 'html.parser')
    log_table = team_log_soup.find('table', {'id': table_type})

    if log_table:
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
                    existing_game_stats = TeamGameLogAdvancedStats.objects.filter(team=team, date=game_data['Date']).first()
                else:
                    existing_game_stats = TeamGameLogGeneralStats.objects.filter(team=team, date=game_data['Date']).first()
           
            if game_data and not existing_game_stats:        
                rank = row.find('th')
                if rank:
                    game_data[columns[0]] = rank.text.strip()  
                    game_data[columns[1]] = index + 1
                
                if log_type == GENERAL_STATS :
                    properties = TeamGameLogGeneralStats.get_properties()
                    cleaned_fields = [field for field in columns if field != '']
                    properties = properties[1:len(properties)-1]

                    game_stats_data = {properties[index]: game_data[cleaned_fields[index]] for index in range(len(cleaned_fields))}
                    game_stats_data["team"] = team
                    game_stats_data["season"] = YEAR
                    sanitize_data(game_stats_data)
                    game_stats = TeamGameLogGeneralStats(
                        **game_stats_data
                    )
                elif log_type == ADVANCED_STATS:
                    properties = TeamGameLogAdvancedStats.get_properties()
                    cleaned_fields = [field for field in columns if field != '']
                    properties = properties[1:len(properties)-1]
                    game_stats_data = {properties[index]: game_data[cleaned_fields[index]] for index in range(len(cleaned_fields))}
                    game_stats_data["team"] = team
                    game_stats_data["season"] = YEAR
                    sanitize_data(game_stats_data)
                    game_stats = TeamGameLogAdvancedStats(
                       **game_stats_data
                    )            
                game_stats.save()
    else:
        print(f"No games log data found for {team}")


