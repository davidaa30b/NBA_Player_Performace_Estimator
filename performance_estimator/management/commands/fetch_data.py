from django.core.management.base import BaseCommand
from performance_estimator.constants import ADVANCED_STATS, GENERAL_STATS, TEAM_FULL_NAMES, TEAMS
from performance_estimator.models import Team
from performance_estimator.scripts.fetch_basketball_players_data import get_player_games_log,get_player_games_log 
from performance_estimator.scripts.fetch_basketball_teams_data import get_team_games_log,get_team_games_log
from performance_estimator.scripts.fetch_pictures import get_picture_team, get_pictures_team_roster
from performance_estimator.scripts.fetch_schedule_data import fetch_schedule_for_team


class Command(BaseCommand):
    help = 'Fetches and saves basketball data from Basketball Reference'

    def handle(self, *args, **kwargs):

        for index, team_abbr in enumerate(TEAMS):
            try:
                team = Team.objects.get(abbreviation=team_abbr)
            except Team.DoesNotExist:
                team = Team(name = TEAM_FULL_NAMES[index],abbreviation = team_abbr)
                team.save()
            #general
            #get_player_games_log(team, GENERAL_STATS)
            #advanced 
            
            #get_player_games_log(team, ADVANCED_STATS)
            # get_team_games_log(team,GENERAL_STATS)
            # get_team_games_log(team,ADVANCED_STATS)
            # fetch_schedule_for_team(team_abbr)
            # get_pictures_team_roster(team)
            
        self.stdout.write(self.style.SUCCESS('Successfully fetched and saved basketball data.'))
