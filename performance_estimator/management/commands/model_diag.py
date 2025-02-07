from graphviz import Digraph
from django.core.management.base import BaseCommand
from performance_estimator.constants import ADVANCED_STATS, GENERAL_STATS, TEAM_FULL_NAMES, TEAMS
from performance_estimator.models import Team
from performance_estimator.scripts.fetch_basketball_players_data import get_player_games_log,get_player_games_log 
from performance_estimator.scripts.fetch_basketball_teams_data import get_team_games_log,get_team_games_log
from performance_estimator.scripts.fetch_schedule_data import fetch_schedule_for_team


class Command(BaseCommand):
    help = 'Fetches and saves basketball data from Basketball Reference'

    def handle(self, *args, **kwargs):
        # Създаване на графика
        dot = Digraph('Django Models', format='png')

        # Дефиниране на класовете
        models = {
            "Team": ["name", "abbreviation"],
            "TeamSchedule": ["date", "location", "opponent", "season"],
            "TeamGameLogGeneralStats": ["team_points", "opponents_points", "team_field_goals", "team_three_pointers"],
            "TeamGameLogAdvancedStats": ["offensive_rating", "defensive_rating", "pace"],
            "Player": ["name"],
            "PlayerSeason": ["year"],
            "GameLogPlayerGeneralStats": ["field_goals", "three_pointers", "assists"],
            "GameLogPlayerAdvancedStats": ["true_shooting_percentage", "usage_rate"],
        }

        # Добавяне на модели в графиката
        for model, fields in models.items():
            label = f"{model}|{' | '.join(fields)}"
            dot.node(model, label=label, shape="record")

        # Връзки между моделите
        relations = [
            ("TeamSchedule", "Team"),
            ("TeamGameLogGeneralStats", "Team"),
            ("TeamGameLogAdvancedStats", "Team"),
            ("PlayerSeason", "Player"),
            ("PlayerSeason", "Team"),
            ("GameLogPlayerGeneralStats", "PlayerSeason"),
            ("GameLogPlayerAdvancedStats", "PlayerSeason"),
        ]

        # Добавяне на релации
        for child, parent in relations:
            dot.edge(child, parent, arrowhead="crow")

        # Запазване на файла
        dot_path = "/mnt/data/django_models_diagram"
        dot.render(dot_path)

        # Връщане на пътя към изображението
        dot_path + ".png"
