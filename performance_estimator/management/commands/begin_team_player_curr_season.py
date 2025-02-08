from django.db.models import Case, When, Value
from django.db import models
from django.core.management.base import BaseCommand

from performance_estimator.models import GameLogPlayerGeneralStats,GameLogPlayerAdvancedStats, Player, PlayerSeason, Team,TeamGameLogAdvancedStats,TeamGameLogGeneralStats,TeamSchedule

class Command(BaseCommand):

   def handle(self, *args, **kwargs):
    players = Player.objects.all()

    for player in players:
        latest_game = GameLogPlayerGeneralStats.objects.filter(player__player=player, season=2025).order_by('-date').first()
        if latest_game is None:
            continue

        team = Team.objects.filter(abbreviation=latest_game.team).first()
        print(player.name, team.name)

        player_season = PlayerSeason.objects.filter(player=player, team=team, year=2025).first()
        if not player_season:
            player_season = PlayerSeason(player=player, team=team, year=2025)
            player_season.save()

        general_stats_logs = GameLogPlayerGeneralStats.objects.filter(player__player=player,team=team.abbreviation, season=2025)
        advanced_stats_logs = GameLogPlayerAdvancedStats.objects.filter(player__player=player,team=team.abbreviation, season=2025)

        for general_log in general_stats_logs:
            general_log.player = player_season 
            general_log.save()

        for advanced_log in advanced_stats_logs:
            advanced_log.player = player_season 
            advanced_log.save()

