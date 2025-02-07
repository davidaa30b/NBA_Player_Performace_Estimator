from enum import Enum


YEAR = 2025
SITE_LINK = 'https://www.basketball-reference.com'


BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

ADVANCED_STATS = 'Advanced Game Log'
GENERAL_STATS = 'Game Log'

LAST_NUMBER_GAMES = 5

#STATS
class Stats(Enum):
    POINTS = 'Points'
    REBOUNDS = 'Rebounds'
    ASSISTS = 'Assists'
    STEALS = 'Steals'
    BLOCKS = 'Blocks'
    GAME_SCORE = "Game_Score"
    
    def __str__(self):
        return self.value 

TEAMS = [
    'ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
    'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
     'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
]


TEAM_FULL_NAMES = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 
    'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 
    'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 
    'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 
    'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks', 
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 
    'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 
    'Utah Jazz', 'Washington Wizards'
]