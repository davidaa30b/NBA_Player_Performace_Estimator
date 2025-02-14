from performance_estimator.constants import YEAR
from performance_estimator.models import Player, PlayerSeason

def get_player_seasons(player_id: int):
    player = Player.objects.get(id=player_id)
    player_seasons = PlayerSeason.objects.prefetch_related().filter(player=player)
    return player,{season.year for season in player_seasons if season.year<YEAR}