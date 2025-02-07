from django.core.management.base import BaseCommand
from performance_estimator.constants import Stats
from performance_estimator.models import Team
from performance_estimator.scripts.predict_player_stat import get_player_stat_model


class Command(BaseCommand):
    help = 'Predicts players stat based on user input'

    def handle(self, *args, **kwargs):
        player_name = "Kevin Durant" 
        
        get_player_stat_model(player_name,True,Stats.POINTS)
        get_player_stat_model(player_name,True,Stats.ASSISTS)
        get_player_stat_model(player_name,True, Stats.BLOCKS)
        get_player_stat_model(player_name,True, Stats.REBOUNDS)
        get_player_stat_model(player_name,True, Stats.STEALS)
        get_player_stat_model(player_name,True, Stats.GAME_SCORE)
    
        self.stdout.write(self.style.SUCCESS(f"Successfully predicted {player_name}'s stats for the next game."))
