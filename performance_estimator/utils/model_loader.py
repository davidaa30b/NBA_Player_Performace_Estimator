from datetime import datetime
from django.db.models import F
import pandas as pd
import numpy as np
from performance_estimator.models import Player, PlayerSeason,Team
from performance_estimator.constants import LAST_NUMBER_GAMES, TEAM_FULL_NAMES, TEAMS, YEAR, Stats
from performance_estimator.utils.minutes_operations import time_to_minutes,minutes_to_average
from performance_estimator.utils.model_initializer import initialize_data


def get_team_advanced_stats(team_abbr: str,input_season):
        if team_abbr:
            team = Team.objects.prefetch_related(
            'teamgamelogadvancedstats'
            ).get(abbreviation=team_abbr)

        team_advanced_stats = team.teamgamelogadvancedstats.filter(season=input_season)

        stats = {
            'defensive_rating': [],
            'pace': [],
            'defensive_effective_field_goal_percentage': [],
            'defensive_turnover_percentage': [],
            'defensive_rebound_percentage': [],
            'defensive_free_throws_per_field_goal_attempt_percentage': []
        }

        for game in team_advanced_stats:
            stats['defensive_rating'].append(game.defensive_rating)
            stats['pace'].append(game.pace)
            stats['defensive_effective_field_goal_percentage'].append(game.defensive_effective_field_goal_percentage)
            stats['defensive_turnover_percentage'].append(game.defensive_turnover_percentage)
            stats['defensive_rebound_percentage'].append(game.defensive_rebound_percentage)
            stats['defensive_free_throws_per_field_goal_attempt_percentage'].append(game.defensive_free_throws_per_field_goal_attempt_percentage)

        return stats

class ModelLoader():


    def __init__(self,player_name,input_season):
        self.season = input_season

        player = Player.objects.get(name=player_name)
        
        season_players = PlayerSeason.objects.prefetch_related(
        'gamelogplayergeneralstats',
        'gamelogplayeradvancedstats',
        ).filter(player=player, year=self.season)

        self.player_general_stats = []
        self.player_advanced_stats = []
        self.team_general_stats = []
        self.team_advanced_stats = []
        schedules = []
        self.player_games_count = 0
        self.team_games_count = 0
        self.season_players_count = season_players.count()
        for season_player in season_players:
            team = Team.objects.prefetch_related(
                'teamgameloggeneralstats',
                'teamgamelogadvancedstats',
                'teamschedule'
            ).get(name=season_player.team.name)
            p_gen_stats = season_player.gamelogplayergeneralstats.filter(season=self.season)
            t_gen_stats = team.teamgameloggeneralstats.filter(season=self.season)
            self.player_general_stats.append(p_gen_stats)
            self.player_advanced_stats.append(season_player.gamelogplayeradvancedstats.filter(season=self.season))

            self.team_general_stats.append(t_gen_stats)
            self.team_advanced_stats.append(team.teamgamelogadvancedstats.filter(season=self.season))

            self.player_games_count = len(p_gen_stats)
            self.team_games_count = len(t_gen_stats)
            schedules.append(team.teamschedule.filter(season=self.season))

        self.team_schedule = schedules[0]
        self.round_index_begin = 0
        self.round_index_end = LAST_NUMBER_GAMES
        self.datas_played = []
        self.minutes_played_games = []
        self.games_started = []
        self.locations_games = []
        self.player_field_goals = []
        self.player_field_goals_attempted = []
        self.player_field_goal_percentage = []
        self.player_three_pointers = []
        self.player_three_pointers_attempted = []
        self.player_three_pointers_percentage = []
        self.player_free_throws = []
        self.player_free_throws_attempted = []
        self.player_free_throw_percentage = []
        self.player_offensive_rebounds = []
        self.player_defensive_rebounds = []
        self.player_total_rebounds = []
        self.player_assists = []
        self.player_steals = []
        self.player_blocks = []
        self.player_turnovers = []
        self.player_personal_fouls = []
        self.player_points = []
        self.player_game_score = []
        self.player_plus_minus = []
        self.player_true_shooting_percentage = []
        self.player_effective_field_goal_percentage = []
        self.player_offensive_rebound_percentage = []
        self.player_defensive_rebound_percentage = []
        self.player_total_rebound_percentage = []
        self.player_assist_percentage = []
        self.player_steal_percentage = []
        self.player_block_percentage = []
        self.player_turnover_percentage = []
        self.player_usage_rate = []
        self.player_offensive_rating = []
        self.player_defensive_rating = []
        self.player_game_score = []
        self.player_plus_minus = []
        self.team_field_goals = []
        self.team_field_goals_attempted = []
        self.team_field_goal_percentage = []
        self.team_three_pointers = []
        self.team_three_pointers_attempted = []
        self.team_three_pointers_percentage = []
        self.team_free_throws = []
        self.team_free_throws_attempted = []
        self.team_free_throw_percentage = []
        self.team_offensive_rebounds = []
        self.team_total_rebounds = []
        self.team_assists = []
        self.team_steals = []
        self.team_blocks = []
        self.team_turnovers = []
        self.team_personal_fouls = []
        self.opponent_names_log = []
        self.opponent_field_goals = []
        self.opponent_field_goals_attempted = []
        self.opponent_field_goal_percentage = []
        self.opponent_three_pointers = []
        self.opponent_three_pointers_attempted = []
        self.opponent_three_pointers_percentage = []
        self.opponent_free_throws = []
        self.opponent_free_throws_attempted = []
        self.opponent_free_throw_percentage = []
        self.opponent_offensive_rebounds = []
        self.opponent_total_rebounds = []
        self.opponent_assists = []
        self.opponent_steals = []
        self.opponent_blocks = []
        self.opponent_turnovers = []
        self.opponent_personal_fouls = []
        self.team_offensive_rating = []
        self.team_defensive_rating = []
        self.team_pace = []
        self.team_free_throw_attempt_rate = []
        self.team_three_point_attempt_rate = []
        self.team_true_shooting_percentage = []
        self.team_total_reboound_percentage = []
        self.team_assist_percentage = []
        self.team_steal_percentage = []
        self.team_block_percentage = []
        self.team_offensive_effective_field_goal_percentage = []
        self.team_offensive_turnover_percentage = []
        self.team_offensive_rebound_percentage = []
        self.team_offensive_free_throws_per_field_goal_attempt_percentage = []
        self.team_defensive_effective_field_goal_percentage = []
        self.team_defensive_turnover_percentage = []
        self.team_defensive_rebound_percentage = []
        self.team_defensive_free_throws_per_field_goal_attempt_percentage = []


    def model_load_data(self, stat = Stats.POINTS ):
        for index in range(0,self.season_players_count):
            for game in self.player_general_stats[index]:
                self.datas_played.append(game.date)
                self.minutes_played_games.append(game.minutes_played)
                self.games_started.append(game.started)
                self.locations_games.append(game.location)
                self.player_field_goals.append(game.field_goals)
                self.player_field_goals_attempted.append(game.field_goals_attempted)
                self.player_field_goal_percentage.append(game.field_goal_percentage)
                self.player_three_pointers.append(game.three_pointers)
                self.player_three_pointers_attempted.append(game.three_pointers_attempted)
                self.player_three_pointers_percentage.append(game.three_pointers_percentage)
                self.player_free_throws.append(game.free_throws)
                self.player_free_throws_attempted.append(game.free_throws_attempted)
                self.player_free_throw_percentage.append(game.free_throw_percentage)
                self.player_offensive_rebounds.append(game.offensive_rebounds)
                self.player_defensive_rebounds.append(game.defensive_rebounds)
                self.player_total_rebounds.append(game.total_rebounds)
                self.player_assists.append(game.assists)
                self.player_steals.append(game.steals)
                self.player_blocks.append(game.blocks)
                self.player_turnovers.append(game.turnovers)
                self.player_personal_fouls.append(game.personal_fouls)
                self.player_points.append(game.points)
                self.player_game_score.append(game.game_score)
                self.player_plus_minus.append(game.plus_minus if game.plus_minus != '' else 0)

            for game in self.player_advanced_stats[index]:
                self.player_true_shooting_percentage.append(game.true_shooting_percentage)
                self.player_effective_field_goal_percentage.append(game.effective_field_goal_percentage)
                self.player_offensive_rebound_percentage.append(game.offensive_rebound_percentage)
                self.player_defensive_rebound_percentage.append(game.defensive_rebound_percentage)
                self.player_total_rebound_percentage.append(game.total_rebound_percentage)
                self.player_assist_percentage.append(game.assist_percentage)
                self.player_steal_percentage.append(game.steal_percentage)
                self.player_block_percentage.append(game.block_percentage)
                self.player_turnover_percentage.append(game.turnover_percentage)
                self.player_usage_rate.append(game.usage_rate)
                self.player_offensive_rating.append(game.offensive_rating)
                self.player_defensive_rating.append(game.defensive_rating)
                self.player_game_score.append(game.game_score)



            for game in self.team_general_stats[index]:
                self.team_field_goals.append(game.team_field_goals)
                self.team_field_goals_attempted.append(game.team_field_goals_attempted)
                self.team_field_goal_percentage.append(game.team_field_goal_percentage)
                self.team_three_pointers.append(game.team_three_pointers)
                self.team_three_pointers_attempted.append(game.team_three_pointers_attempted)
                self.team_three_pointers_percentage.append(game.team_three_pointers_percentage)
                self.team_free_throws.append(game.team_free_throws)
                self.team_free_throws_attempted.append(game.team_free_throws_attempted)
                self.team_free_throw_percentage.append(game.team_free_throw_percentage)
                self.team_offensive_rebounds.append(game.team_offensive_rebounds)
                self.team_total_rebounds.append(game.team_total_rebounds)
                self.team_assists.append(game.team_assists)
                self.team_steals.append(game.team_steals)
                self.team_blocks.append(game.team_blocks)
                self.team_turnovers.append(game.team_turnovers)
                self.team_personal_fouls.append(game.team_personal_fouls)
                self.opponent_names_log.append(game.opponent)
                self.opponent_field_goals.append(game.opponent_field_goals)
                self.opponent_field_goals_attempted.append(game.opponent_field_goals_attempted)
                self.opponent_field_goal_percentage.append(game.opponent_field_goal_percentage)
                self.opponent_three_pointers.append(game.opponent_three_pointers)
                self.opponent_three_pointers_attempted.append(game.opponent_three_pointers_attempted)
                self.opponent_three_pointers_percentage.append(game.opponent_three_pointers_percentage)
                self.opponent_free_throws.append(game.opponent_free_throws)
                self.opponent_free_throws_attempted.append(game.opponent_free_throws_attempted)
                self.opponent_free_throw_percentage.append(game.opponent_free_throw_percentage)
                self.opponent_offensive_rebounds.append(game.opponent_offensive_rebounds)
                self.opponent_total_rebounds.append(game.opponent_total_rebounds)
                self.opponent_assists.append(game.opponent_assists)
                self.opponent_steals.append(game.opponent_steals)
                self.opponent_blocks.append(game.opponent_blocks)
                self.opponent_turnovers.append(game.opponent_turnovers)
                self.opponent_personal_fouls.append(game.opponent_personal_fouls)

            for game in self.team_advanced_stats[index]:
                self.team_offensive_rating.append(game.offensive_rating)
                self.team_defensive_rating.append(game.defensive_rating)
                self.team_pace.append(game.pace)
                self.team_free_throw_attempt_rate.append(game.free_throw_attempt_rate)
                self.team_three_point_attempt_rate.append(game.three_point_attempt_rate)
                self.team_true_shooting_percentage.append(game.true_shooting_percentage)
                self.team_total_reboound_percentage.append(game.total_reboound_percentage)
                self.team_assist_percentage.append(game.assist_percentage)
                self.team_steal_percentage.append(game.steal_percentage)
                self.team_block_percentage.append(game.block_percentage)
                self.team_offensive_effective_field_goal_percentage.append(game.offensive_effective_field_goal_percentage)
                self.team_offensive_turnover_percentage.append(game.offensive_turnover_percentage)
                self.team_offensive_rebound_percentage.append(game.offensive_rebound_percentage)
                self.team_offensive_free_throws_per_field_goal_attempt_percentage.append(game.offensive_free_throws_per_field_goal_attempt_percentage)
                self.team_defensive_effective_field_goal_percentage.append(game.defensive_effective_field_goal_percentage)
                self.team_defensive_turnover_percentage.append(game.defensive_turnover_percentage)
                self.team_defensive_rebound_percentage.append(game.defensive_rebound_percentage)
                self.team_defensive_free_throws_per_field_goal_attempt_percentage.append(game.defensive_free_throws_per_field_goal_attempt_percentage)

        data = initialize_data(LAST_NUMBER_GAMES)
        for game in range(LAST_NUMBER_GAMES,self.player_games_count):
            data['date'].append(self.datas_played[game])
            data['rest_days_prior'].append((self.datas_played[game]-self.datas_played[game-1]).days)
            data['location'].append(self.locations_games[game])
            data[ f'minutes_played'].append(minutes_to_average(self.minutes_played_games[:self.round_index_end]))
            data[ f'minutes_played_last{LAST_NUMBER_GAMES}'].append(minutes_to_average(self.minutes_played_games[self.round_index_begin:self.round_index_end]))
            data['started'].append(self.games_started[game])
            data[ f'player_ppg'].append(np.mean(self.player_points[:self.round_index_end]))
            data[ f'player_ppg_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_points[self.round_index_begin:self.round_index_end]))
            data['player_field_goals'].append(np.mean(self.player_field_goals[:self.round_index_end]))
            data[ f'player_field_goals_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goals[self.round_index_begin:self.round_index_end]))
            data[ f'player_field_goals_attempted'].append(np.mean(self.player_field_goals_attempted[:self.round_index_end]))
            data[ f'player_field_goals_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goals_attempted[self.round_index_begin:self.round_index_end]))
            data[ f'player_field_goal_percentage'].append(np.mean(self.player_field_goal_percentage[:self.round_index_end]))
            data[ f'player_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goal_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_three_pointers'].append(np.mean(self.player_three_pointers[:self.round_index_end]))
            data[ f'player_three_pointers_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers[self.round_index_begin:self.round_index_end]))
            data[ f'player_three_pointers_attempted'].append(np.mean(self.player_three_pointers_attempted[:self.round_index_end]))
            data[ f'player_three_pointers_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers_attempted[self.round_index_begin:self.round_index_end]))
            data[ f'player_three_pointers_percentage'].append(np.mean(self.player_three_pointers_percentage[:self.round_index_end]))
            data[ f'player_three_pointers_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_free_throws'].append(np.mean(self.player_free_throws[:self.round_index_end]))
            data[ f'player_free_throws_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throws[self.round_index_begin:self.round_index_end]))
            data[ f'player_free_throws_attempted'].append(np.mean(self.player_free_throws_attempted[:self.round_index_end]))
            data[ f'player_free_throws_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throws_attempted[self.round_index_begin:self.round_index_end]))
            data[ f'player_free_throw_percentage'].append(np.mean(self.player_free_throw_percentage[:self.round_index_end]))
            data[ f'player_free_throw_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throw_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_total_rebounds'].append(np.mean(self.player_total_rebounds[self.round_index_begin:self.round_index_end]))
            data[ f'player_total_rebounds_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_total_rebounds[:self.round_index_end]))
            data[ f'player_assists'].append(np.mean(self.player_assists[self.round_index_begin:self.round_index_end]))
            data[ f'player_assists_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_assists[:self.round_index_end]))
            data[ f'player_steals'].append(np.mean(self.player_steals[self.round_index_begin:self.round_index_end]))
            data[ f'player_steals_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_steals[:self.round_index_end]))
            data[ f'player_blocks'].append(np.mean(self.player_blocks[self.round_index_begin:self.round_index_end]))
            data[ f'player_blocks_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_blocks[:self.round_index_end]))
            data[ f'player_turnovers'].append(np.mean(self.player_turnovers[self.round_index_begin:self.round_index_end]))
            data[ f'player_turnovers_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_turnovers[:self.round_index_end]))
            data[ f'player_game_score'].append(np.mean(self.player_game_score[:self.round_index_end]))
            data[ f'player_game_score_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_game_score[self.round_index_begin:self.round_index_end]))
            data[ f'player_personal_fouls'].append(np.mean(self.player_personal_fouls[:self.round_index_end]))
            data[ f'player_personal_fouls_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_personal_fouls[self.round_index_begin:self.round_index_end]))
            data[ f'player_plus_minus'].append(np.mean([int(pm) for pm in self.player_plus_minus[:self.round_index_end]]))
            data[ f'player_plus_minus_last{LAST_NUMBER_GAMES}'].append(np.mean([int(pm) for pm in self.player_plus_minus[self.round_index_begin:self.round_index_end]]))
            data[ f'player_true_shooting_percentage'].append(np.mean(self.player_true_shooting_percentage[:self.round_index_end]))
            data[ f'player_true_shooting_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_true_shooting_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_effective_field_goal_percentage'].append(np.mean(self.player_effective_field_goal_percentage[:self.round_index_end]))
            data[ f'player_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_total_rebound_percentage'].append(np.mean(self.player_total_rebound_percentage[:self.round_index_end]))
            data[ f'player_total_rebound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_total_rebound_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_assist_percentage'].append(np.mean(self.player_assist_percentage[:self.round_index_end]))
            data[ f'player_assist_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_assist_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_steal_percentage'].append(np.mean(self.player_steal_percentage[:self.round_index_end]))
            data[ f'player_steal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_steal_percentage[self.round_index_begin:self.round_index_end]))        
            data[ f'player_block_percentage'].append(np.mean(self.player_block_percentage[:self.round_index_end]))
            data[ f'player_block_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_block_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_turnover_percentage'].append(np.mean(self.player_turnover_percentage[:self.round_index_end]))
            data[ f'player_turnover_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_turnover_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'player_offensive_rating'].append(np.mean(self.player_offensive_rating[:self.round_index_end]))
            data[ f'player_offensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_offensive_rating[self.round_index_begin:self.round_index_end]))
            data[ f'player_defensive_rating'].append(np.mean(self.player_defensive_rating[:self.round_index_end]))
            data[ f'player_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_defensive_rating[self.round_index_begin:self.round_index_end]))
            data[ f'player_usage_rate'].append(np.mean(self.player_usage_rate[:self.round_index_end]))
            data[ f'player_usage_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_usage_rate[self.round_index_begin:self.round_index_end]))
            data[ f'team_offensive_rating'].append(np.mean(self.team_offensive_rating[:self.round_index_end]))
            data[ f'team_offensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_rating[self.round_index_begin:self.round_index_end]))
            data[ f'team_defensive_rating'].append(np.mean(self.team_defensive_rating[:self.round_index_end]))
            data[ f'team_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_rating[self.round_index_begin:self.round_index_end]))
            data[ f'team_pace'].append(np.mean(self.team_pace[:self.round_index_end]))
            data[ f'team_pace_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_pace[self.round_index_begin:self.round_index_end]))
            data[ f'team_free_throw_attempt_rate'].append(np.mean(self.team_free_throw_attempt_rate[:self.round_index_end]))
            data[ f'team_free_throw_attempt_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_free_throw_attempt_rate[self.round_index_begin:self.round_index_end]))
            data[ f'team_three_point_attempt_rate'].append(np.mean(self.team_three_point_attempt_rate[:self.round_index_end]))
            data[ f'team_three_point_attempt_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_three_point_attempt_rate[self.round_index_begin:self.round_index_end]))
            data[ f'team_true_shooting_percentage'].append(np.mean(self.team_true_shooting_percentage[:self.round_index_end]))
            data[ f'team_true_shooting_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_true_shooting_percentage[:self.round_index_end]))
            data[ f'team_total_reboound_percentage'].append(np.mean(self.team_total_reboound_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_total_reboound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_total_reboound_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_assist_percentage'].append(np.mean(self.team_assist_percentage[:self.round_index_end]))
            data[ f'team_assist_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_assist_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_steal_percentage'].append(np.mean(self.team_steal_percentage[:self.round_index_end]))
            data[ f'team_steal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_steal_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_offensive_effective_field_goal_percentage'].append(np.mean(self.team_offensive_effective_field_goal_percentage[:self.round_index_end]))
            data[ f'team_offensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_offensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(self.team_offensive_free_throws_per_field_goal_attempt_percentage[:self.round_index_end]))
            data[ f'team_offensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_free_throws_per_field_goal_attempt_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_defensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(self.team_defensive_free_throws_per_field_goal_attempt_percentage[:self.round_index_end]))
            data[ f'team_defensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_free_throws_per_field_goal_attempt_percentage[self.round_index_begin:self.round_index_end]))
            data[ f'team_defensive_effective_field_goal_percentage'].append(np.mean(self.team_defensive_effective_field_goal_percentage[:self.round_index_end]))
            data[ f'team_defensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
            
            opponent = self.opponent_names_log[game]
            opponent_stats = get_team_advanced_stats(opponent,self.season)
            data[ 'opponent'].append(TEAMS.index(opponent))
            data[ 'opponent_defensive_rating'].append(np.mean(opponent_stats['defensive_rating'][:self.round_index_end]))
            data[ f'opponent_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_rating'][self.round_index_begin:self.round_index_end]))
            data[ 'opponent_pace'].append(np.mean(opponent_stats['pace'][:self.round_index_end]))
            data[ f'opponent_pace_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['pace'][:self.round_index_end]))
            data[ 'opponent_defensive_effective_field_goal_percentage'].append(np.mean(opponent_stats['defensive_effective_field_goal_percentage'][:self.round_index_end]))
            data[ f'opponent_defensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_effective_field_goal_percentage'][self.round_index_begin:self.round_index_end]))
            data[ f'opponent_defensive_turnover_percentage'].append(np.mean(opponent_stats['defensive_turnover_percentage'][:self.round_index_end]))
            data[ f'opponent_defensive_turnover_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_turnover_percentage'][self.round_index_begin:self.round_index_end]))
            data[ f'opponent_defensive_rebound_percentage'].append(np.mean(opponent_stats['defensive_rebound_percentage'][:self.round_index_end]))
            data[ f'opponent_defensive_rebound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_rebound_percentage'][self.round_index_begin:self.round_index_end]))
            data[ f'opponent_defensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(opponent_stats['defensive_free_throws_per_field_goal_attempt_percentage'][:self.round_index_end]))
            data[ f'opponent_defensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_free_throws_per_field_goal_attempt_percentage'][self.round_index_begin:self.round_index_end]))
            points_vs_opp = [points_for_game for index,points_for_game in enumerate(self.player_points[:game]) if opponent == self.opponent_names_log[index] ]
            assits_vs_opp = [assits_for_game for index,assits_for_game in enumerate(self.player_assists[:game]) if opponent == self.opponent_names_log[index] ]
            blocks_vs_opp = [blocks_for_game for index,blocks_for_game in enumerate(self.player_blocks[:game]) if opponent == self.opponent_names_log[index] ]
            steals_vs_opp = [steals_for_game for index,steals_for_game in enumerate(self.player_steals[:game]) if opponent == self.opponent_names_log[index] ]
            rebounds_vs_opp = [rebounds_for_game for index,rebounds_for_game in enumerate(self.player_total_rebounds[:game]) if opponent == self.opponent_names_log[index] ]
            game_score_vs_opp = [game_score_for_game for index,game_score_for_game in enumerate(self.player_game_score[:game]) if opponent == self.opponent_names_log[index] ]
            data[ f'points_against_opponent'].append(np.mean(points_vs_opp) if points_vs_opp else 0)
            data[ f'assists_against_opponent'].append(np.mean(assits_vs_opp) if assits_vs_opp else 0)
            data[ f'blocks_against_opponent'].append(np.mean(blocks_vs_opp) if blocks_vs_opp else 0)
            data[ f'steals_against_opponent'].append(np.mean(steals_vs_opp) if steals_vs_opp else 0)
            data[ f'rebounds_against_opponent'].append(np.mean(rebounds_vs_opp) if rebounds_vs_opp else 0)
            data[ f'game_score_against_opponent'].append(np.mean(game_score_vs_opp) if game_score_vs_opp else 0)
            match stat:
                case Stats.POINTS: 
                    data[ f'target'].append(self.player_points[game])                 
                case Stats.ASSISTS: 
                    data[ f'target'].append(self.player_assists[game])
                case Stats.BLOCKS:
                    data[ f'target'].append(self.player_blocks[game])
                case Stats.STEALS:
                    data[ f'target'].append(self.player_steals[game])
                case Stats.REBOUNDS:
                    data[ f'target'].append(self.player_total_rebounds[game])
                case Stats.GAME_SCORE:
                    result = self.player_game_score[game] 
                    data[ f'target'].append(round(result, 3))

            self.round_index_begin+=1
            self.round_index_end+=1


        # pd.set_option('display.max_columns', None)  
        # pd.set_option('display.max_rows', None)    
        # print(pd.DataFrame(data))

        
        return pd.DataFrame(data)
    def model_loader_predict_data(self,starts):
        
        to_be_predicted = initialize_data(LAST_NUMBER_GAMES)
        # print(self.team_games_count)
        # print(self.player_games_count)
        # print(len(self.team_schedule))
        date = self.team_schedule[self.team_games_count:][0].date
        location = self.team_schedule[self.team_games_count:][0].location
        oppponent_full_name = self.team_schedule[self.team_games_count:][0].opponent

        # print(f'Date : {date}\n Location : {"Home" if location else "Away"}\n Position : {"Starter" if starts else "Bench"}\n Opponent : {oppponent_full_name}')
        to_be_predicted['date'].append(date)
        to_be_predicted['rest_days_prior'].append((date - self.datas_played[self.player_games_count-1]).days)
        to_be_predicted['location'].append(location)
        to_be_predicted[ f'minutes_played'].append(minutes_to_average(self.minutes_played_games[:self.round_index_end]))
        to_be_predicted[ f'minutes_played_last{LAST_NUMBER_GAMES}'].append(minutes_to_average(self.minutes_played_games[self.round_index_begin:self.round_index_end]))
        to_be_predicted['started'].append(starts)
        to_be_predicted[ f'player_ppg'].append(np.mean(self.player_points[:self.round_index_end]))
        to_be_predicted[ f'player_ppg_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_points[self.round_index_begin:self.round_index_end]))
        to_be_predicted['player_field_goals'].append(np.mean(self.player_field_goals[:self.round_index_end]))
        to_be_predicted[ f'player_field_goals_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goals[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_field_goals_attempted'].append(np.mean(self.player_field_goals_attempted[:self.round_index_end]))
        to_be_predicted[ f'player_field_goals_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goals_attempted[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_field_goal_percentage'].append(np.mean(self.player_field_goal_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_field_goal_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers'].append(np.mean(self.player_three_pointers[:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers_attempted'].append(np.mean(self.player_three_pointers_attempted[:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers_attempted[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers_percentage'].append(np.mean(self.player_three_pointers_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_three_pointers_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_three_pointers_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_free_throws'].append(np.mean(self.player_free_throws[:self.round_index_end]))
        to_be_predicted[ f'player_free_throws_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throws[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_free_throws_attempted'].append(np.mean(self.player_free_throws_attempted[:self.round_index_end]))
        to_be_predicted[ f'player_free_throws_attempted_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throws_attempted[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_free_throw_percentage'].append(np.mean(self.player_free_throw_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_free_throw_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_free_throw_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_total_rebounds'].append(np.mean(self.player_total_rebounds[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_total_rebounds_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_total_rebounds[:self.round_index_end]))
        to_be_predicted[ f'player_assists'].append(np.mean(self.player_assists[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_assists_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_assists[:self.round_index_end]))
        to_be_predicted[ f'player_steals'].append(np.mean(self.player_steals[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_steals_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_steals[:self.round_index_end]))
        to_be_predicted[ f'player_blocks'].append(np.mean(self.player_blocks[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_blocks_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_blocks[:self.round_index_end]))
        to_be_predicted[ f'player_turnovers'].append(np.mean(self.player_turnovers[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_turnovers_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_turnovers[:self.round_index_end]))
        to_be_predicted[ f'player_game_score'].append(np.mean(self.player_game_score[:self.round_index_end]))
        to_be_predicted[ f'player_game_score_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_game_score[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_personal_fouls'].append(np.mean(self.player_personal_fouls[:self.round_index_end]))
        to_be_predicted[ f'player_personal_fouls_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_personal_fouls[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_plus_minus'].append(np.mean([int(pm) for pm in self.player_plus_minus[:self.round_index_end]]))
        to_be_predicted[ f'player_plus_minus_last{LAST_NUMBER_GAMES}'].append(np.mean([int(pm) for pm in self.player_plus_minus[self.round_index_begin:self.round_index_end]]))
        to_be_predicted[ f'player_true_shooting_percentage'].append(np.mean(self.player_true_shooting_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_true_shooting_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_true_shooting_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_effective_field_goal_percentage'].append(np.mean(self.player_effective_field_goal_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_total_rebound_percentage'].append(np.mean(self.player_total_rebound_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_total_rebound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_total_rebound_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_assist_percentage'].append(np.mean(self.player_assist_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_assist_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_assist_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_steal_percentage'].append(np.mean(self.player_steal_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_steal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_steal_percentage[self.round_index_begin:self.round_index_end]))        
        to_be_predicted[ f'player_block_percentage'].append(np.mean(self.player_block_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_block_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_block_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_turnover_percentage'].append(np.mean(self.player_turnover_percentage[:self.round_index_end]))
        to_be_predicted[ f'player_turnover_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_turnover_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_offensive_rating'].append(np.mean(self.player_offensive_rating[:self.round_index_end]))
        to_be_predicted[ f'player_offensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_offensive_rating[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_defensive_rating'].append(np.mean(self.player_defensive_rating[:self.round_index_end]))
        to_be_predicted[ f'player_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_defensive_rating[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'player_usage_rate'].append(np.mean(self.player_usage_rate[:self.round_index_end]))
        to_be_predicted[ f'player_usage_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.player_usage_rate[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_offensive_rating'].append(np.mean(self.team_offensive_rating[:self.round_index_end]))
        to_be_predicted[ f'team_offensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_rating[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_defensive_rating'].append(np.mean(self.team_defensive_rating[:self.round_index_end]))
        to_be_predicted[ f'team_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_rating[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_pace'].append(np.mean(self.team_pace[:self.round_index_end]))
        to_be_predicted[ f'team_pace_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_pace[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_free_throw_attempt_rate'].append(np.mean(self.team_free_throw_attempt_rate[:self.round_index_end]))
        to_be_predicted[ f'team_free_throw_attempt_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_free_throw_attempt_rate[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_three_point_attempt_rate'].append(np.mean(self.team_three_point_attempt_rate[:self.round_index_end]))
        to_be_predicted[ f'team_three_point_attempt_rate_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_three_point_attempt_rate[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_true_shooting_percentage'].append(np.mean(self.team_true_shooting_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_true_shooting_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_true_shooting_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_total_reboound_percentage'].append(np.mean(self.team_total_reboound_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_total_reboound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_total_reboound_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_assist_percentage'].append(np.mean(self.team_assist_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_assist_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_assist_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_steal_percentage'].append(np.mean(self.team_steal_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_steal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_steal_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_offensive_effective_field_goal_percentage'].append(np.mean(self.team_offensive_effective_field_goal_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_offensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_offensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(self.team_offensive_free_throws_per_field_goal_attempt_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_offensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_offensive_free_throws_per_field_goal_attempt_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_defensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(self.team_defensive_free_throws_per_field_goal_attempt_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_defensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_free_throws_per_field_goal_attempt_percentage[self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'team_defensive_effective_field_goal_percentage'].append(np.mean(self.team_defensive_effective_field_goal_percentage[:self.round_index_end]))
        to_be_predicted[ f'team_defensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(self.team_defensive_effective_field_goal_percentage[self.round_index_begin:self.round_index_end]))
        
        
        opponent_abbr = TEAMS[TEAM_FULL_NAMES.index(oppponent_full_name)]
        opponent_stats = get_team_advanced_stats(opponent_abbr,self.season)
        to_be_predicted[ 'opponent'].append(TEAMS.index(opponent_abbr))
        to_be_predicted[ 'opponent_defensive_rating'].append(np.mean(opponent_stats['defensive_rating'][:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_rating_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_rating'][self.round_index_begin:self.round_index_end]))
        to_be_predicted[ 'opponent_pace'].append(np.mean(opponent_stats['pace'][:self.round_index_end]))
        to_be_predicted[ f'opponent_pace_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['pace'][:self.round_index_end]))
        to_be_predicted[ 'opponent_defensive_effective_field_goal_percentage'].append(np.mean(opponent_stats['defensive_effective_field_goal_percentage'][:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_effective_field_goal_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_effective_field_goal_percentage'][self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_turnover_percentage'].append(np.mean(opponent_stats['defensive_turnover_percentage'][:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_turnover_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_turnover_percentage'][self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_rebound_percentage'].append(np.mean(opponent_stats['defensive_rebound_percentage'][:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_rebound_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_rebound_percentage'][self.round_index_begin:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_free_throws_per_field_goal_attempt_percentage'].append(np.mean(opponent_stats['defensive_free_throws_per_field_goal_attempt_percentage'][:self.round_index_end]))
        to_be_predicted[ f'opponent_defensive_free_throws_per_field_goal_attempt_percentage_last{LAST_NUMBER_GAMES}'].append(np.mean(opponent_stats['defensive_free_throws_per_field_goal_attempt_percentage'][self.round_index_begin:self.round_index_end]))
        
        points_vs_opp = [points_for_game for index,points_for_game in enumerate(self.player_points[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        assits_vs_opp = [assits_for_game for index,assits_for_game in enumerate(self.player_assists[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        blocks_vs_opp = [blocks_for_game for index,blocks_for_game in enumerate(self.player_blocks[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        steals_vs_opp = [steals_for_game for index,steals_for_game in enumerate(self.player_steals[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        rebounds_vs_opp = [rebounds_for_game for index,rebounds_for_game in enumerate(self.player_total_rebounds[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        game_score_vs_opp = [game_score_for_game for index,game_score_for_game in enumerate(self.player_game_score[:self.player_games_count]) if opponent_abbr == self.opponent_names_log[index] ]
        
        to_be_predicted[ f'points_against_opponent'].append(np.mean(points_vs_opp) if points_vs_opp else 0)
        to_be_predicted[ f'assists_against_opponent'].append(np.mean(assits_vs_opp) if assits_vs_opp else 0)
        to_be_predicted[ f'blocks_against_opponent'].append(np.mean(blocks_vs_opp) if blocks_vs_opp else 0)
        to_be_predicted[ f'steals_against_opponent'].append(np.mean(steals_vs_opp) if steals_vs_opp else 0)
        to_be_predicted[ f'rebounds_against_opponent'].append(np.mean(rebounds_vs_opp) if rebounds_vs_opp else 0)
        to_be_predicted[ f'game_score_against_opponent'].append(np.mean(game_score_vs_opp) if game_score_vs_opp else 0)
        to_be_predicted[ f'target'].append('NaN')
        
        
        return pd.DataFrame(to_be_predicted),date,location,oppponent_full_name