import time
import requests
from bs4 import BeautifulSoup
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR
from performance_estimator.models import Player, Team


def get_picture_team(team: Team):
    team_name = team.abbreviation
    team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}.html"
    print(f'{team_name} picture fetching')
    time.sleep(2) 
    response = requests.get(team_url,headers= BROWSER_HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        team_image = soup.find('img', {'class': 'teamlogo'})
        if team_image:
            if not team.image:
                team.image = team_image.get('src')
                team.save()
            else:
                print(f'Image already fetched for {team_name}')
        else:
            print(f'Image not found for {team_name}')

import time
import requests
from bs4 import BeautifulSoup
from performance_estimator.constants import BROWSER_HEADERS, SITE_LINK, YEAR
from performance_estimator.models import Player, Team


def get_player_picture(player_url, player_name):
    response = requests.get(player_url, headers=BROWSER_HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page for {player_name}. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    info_div = soup.find('div', {'id': 'info', 'class': 'players'})
    
    if info_div:
        player_picture = info_div.find('img')
        if player_picture:
            return player_picture.get('src')

    print(f"Could not find picture for {player_name}")
    return None


def get_pictures_team_roster(team: Team):
    team_name: str = team.abbreviation
    print(f'{team_name} pictures for players fetching')

    team_url = f"{SITE_LINK}/teams/{team_name}/{YEAR}.html"
    time.sleep(2)
    response = requests.get(team_url, headers=BROWSER_HEADERS)
    
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
    
    for player_link, player_name in player_links:
        time.sleep(2)
        print(player_link, player_name)
        player = Player.objects.get(name=player_name)
        if not player.image:
            player_image_url = get_player_picture(player_link, player_name)
            if player_image_url:
                    player.image = player_image_url
                    player.save()
            else:
                print(f"{player_name} could not get a picture")

        else:
            print(f"{player_name} already has a picture")
