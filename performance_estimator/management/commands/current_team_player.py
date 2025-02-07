from django.db.models import Case, When, Value
from django.db import models
from django.core.management.base import BaseCommand

from performance_estimator.models import GameLogPlayerGeneralStats,GameLogPlayerAdvancedStats, Player, Team,TeamGameLogAdvancedStats,TeamGameLogGeneralStats,TeamSchedule

class Command(BaseCommand):
    help = 'Fetches and saves basketball data from Basketball Reference'

    def handle(self, *args, **kwargs):
        # GameLogPlayerGeneralStats.objects.all().update(
        #     location=Case(
        #         When(location='@', then=Value(False)),  
        #         default=Value(True),                    
        #         output_field=models.BooleanField()      
        #     )
        # )
        # GameLogPlayerAdvancedStats.objects.all().update(
        #     location=Case(
        #         When(location='@', then=Value(False)),  
        #         default=Value(True),                    
        #         output_field=models.BooleanField()      
        #     )
        # )
        # TeamGameLogGeneralStats.objects.all().update(
        #     location=Case(
        #         When(location='@', then=Value(False)),  
        #         default=Value(True),                    
        #         output_field=models.BooleanField()      
        #     )
        # )
        # TeamGameLogAdvancedStats.objects.all().update(
        #     location=Case(
        #         When(location='@', then=Value(False)),  
        #         default=Value(True),                    
        #         output_field=models.BooleanField()      
        #     )
        # )
        # TeamSchedule.objects.all().update(
        #     location=Case(
        #         When(location='@', then=Value(False)),  
        #         default=Value(True),                    
        #         output_field=models.BooleanField()      
        #     )
        # )    players = Player.objects.all()
        players = Player.objects.all()

        for player in players:
            latest_game = GameLogPlayerGeneralStats.objects.filter(player__player=player).order_by('-date').first()

            if latest_game:
                team_abbreviation = latest_game.team 
                
                team = Team.objects.filter(abbreviation=team_abbreviation).first()

                if team:
                    player.current_team = team
                    player.save()
                    print(f"Updated {player.name}'s current team to {team.name}")