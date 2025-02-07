import requests
from bs4 import BeautifulSoup
from datetime import datetime

from performance_estimator.constants import SITE_LINK, YEAR
from performance_estimator.models import Team, TeamSchedule

def fetch_schedule_for_team(team_abbr):
    print(team_abbr,"schedule fetch")
    url = f'{SITE_LINK}/teams/{team_abbr}/{YEAR}_games.html'
    team = Team.objects.get(abbreviation=team_abbr)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {'id': 'games'})

    properties = TeamSchedule.get_properties()[1:]

    desired_indexes = [0,4,5]

    for row in table.find_all('tr')[1:]:
        cols = [col.text.strip() for col in row.find_all('td')]
        if cols:
            game_data = {
                properties[hi]: (datetime.strptime(cols[ci], '%a, %b %d, %Y').strftime('%Y-%m-%d') if ci == 0 else cols[ci])
                for hi, ci in zip(range(len(properties)), desired_indexes)
            }
            game_data['location'] =  game_data['location'] != '@' #True if Home

            existing_game_data = TeamSchedule.objects.filter(team=team, date=game_data['date']).first()

            if not existing_game_data:
                game_data['team'] = team
                game_data["season"] = YEAR

                game_stats = TeamSchedule(
                        **game_data
                    )
                game_stats.save()
