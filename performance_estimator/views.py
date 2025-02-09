from django.http import JsonResponse
from django.core.management import call_command
from django.shortcuts import render,get_object_or_404
from performance_estimator.constants import YEAR, Stats
from django.db.models import Avg


from performance_estimator.models import GameLogPlayerAdvancedStats, GameLogPlayerGeneralStats, Player, PlayerSeason, Team, TeamGameLogAdvancedStats, TeamGameLogGeneralStats, TeamSchedule
from performance_estimator.scripts.error_estimate_player_stats import graph_player_stat
from performance_estimator.scripts.predict_player_stat import get_player_stat_model
from performance_estimator.utils.minutes_operations import minutes_to_average_print

def team_list(request):
    teams = Team.objects.all()  # Fetch all teams from the database
    return render(request, 'teams.html', {'teams': teams})  # Corrected template paths})

def get_all_seasons_for_team(team_id):
    general_stats_seasons = TeamGameLogGeneralStats.objects.filter(team_id=team_id).values_list('season', flat=True).distinct()
    
    all_seasons = set(general_stats_seasons) 
    
    sorted_seasons = sorted(all_seasons)

    return sorted_seasons

def team_profile(request, team_id):
    team = get_object_or_404(Team, id=team_id) 
    players_seasons = PlayerSeason.objects.filter(team=team, year=YEAR)
    players = []
    for player_season in players_seasons:
        if player_season.player.current_team == team:
            players.append(player_season.player)

    seasons_years = get_all_seasons_for_team(team_id)
    general_stats_logs_avg = {}
    advanced_stats_logs_avg = {}

    for season in seasons_years:
        game_logs_gen = TeamGameLogGeneralStats.objects.filter(team=team,season=season)
        avg_stats = game_logs_gen.aggregate(
            team_field_goals =Avg('team_field_goals'),
            team_field_goals_attempted = Avg('team_field_goals_attempted'),
            team_field_goal_percentage =Avg('team_field_goal_percentage'),
            team_three_pointers = Avg('team_three_pointers'),
            team_three_pointers_attempted = Avg('team_three_pointers_attempted'),
            team_three_pointers_percentage = Avg('team_three_pointers_percentage'),
            team_free_throws = Avg('team_free_throws'),
            team_free_throws_attempted = Avg('team_free_throws_attempted'),
            team_free_throw_percentage = Avg('team_free_throw_percentage'),
            team_offensive_rebounds = Avg('team_offensive_rebounds'),
            team_total_rebounds = Avg('team_total_rebounds'),
            team_assists = Avg('team_assists'),
            team_steals = Avg('team_steals'),
            team_blocks = Avg('team_blocks'),
            team_turnovers = Avg('team_turnovers'),
            team_personal_fouls = Avg('team_personal_fouls'),
        )
        general_stats_logs_avg[season] = avg_stats
        
        game_logs_adv = TeamGameLogAdvancedStats.objects.filter(team=team,season=season)
        avg_stats = game_logs_adv.aggregate(
            offensive_rating =Avg('offensive_rating'),
            defensive_rating = Avg('defensive_rating'),
            pace =Avg('pace'),
            free_throw_attempt_rate = Avg('free_throw_attempt_rate'),
            three_point_attempt_rate = Avg('three_point_attempt_rate'),
            true_shooting_percentage = Avg('true_shooting_percentage'),
            total_reboound_percentage = Avg('total_reboound_percentage'),
            assist_percentage = Avg('assist_percentage'),
            steal_percentage = Avg('steal_percentage'),
            block_percentage = Avg('block_percentage'),
            offensive_effective_field_goal_percentage = Avg('offensive_effective_field_goal_percentage'),
            offensive_turnover_percentage = Avg('offensive_turnover_percentage'),
            offensive_rebound_percentage = Avg('offensive_rebound_percentage'),
            offensive_free_throws_per_field_goal_attempt_percentage = Avg('offensive_free_throws_per_field_goal_attempt_percentage'),
            defensive_effective_field_goal_percentage = Avg('defensive_effective_field_goal_percentage'),
            defensive_turnover_percentage = Avg('defensive_turnover_percentage'),
            defensive_rebound_percentage = Avg('defensive_rebound_percentage'),
            defensive_free_throws_per_field_goal_attempt_percentage = Avg('defensive_free_throws_per_field_goal_attempt_percentage'),
        )
        advanced_stats_logs_avg[season] = avg_stats

        selected_year = request.GET.get('season')
        selected_year = YEAR if selected_year is None else selected_year

        full_season_general = TeamGameLogGeneralStats.objects.filter(team=team,season=selected_year).order_by('-date')
        full_season_advanced = TeamGameLogAdvancedStats.objects.filter(team=team,season=selected_year).order_by('-date')


    return render(request, 'team_profile.html', 
                  {'team': team, 
                   'players': players,
                   'seasons_years':seasons_years,
                   'general_stats_logs_avg':general_stats_logs_avg,
                   'advanced_stats_logs_avg':advanced_stats_logs_avg,
                   'full_season_general':full_season_general,
                   'full_season_advanced':full_season_advanced
    })


def player_profile(request, team_id, player_id):
    player = get_object_or_404(Player, id=player_id)
    
    player_seasons = PlayerSeason.objects.filter(player=player).order_by('-year')
    career_averages_gen_stats = {}
    career_averages_adv_stats = {}
    for player_season in player_seasons:
        game_logs = GameLogPlayerGeneralStats.objects.filter(player=player_season,team=player_season.team.abbreviation)
        minutes_played = [log.minutes_played for log in game_logs]
        avg_minutes = minutes_to_average_print(minutes_played)
        avg_stats = game_logs.aggregate(
            avg_points=Avg('points'),
            avg_field_goal_percentage=Avg('field_goal_percentage'),
            avg_three_pointers_percentage=Avg('three_pointers_percentage'),
            avg_free_throw_percentage=Avg('free_throw_percentage'),
            avg_assists=Avg('assists'),
            avg_offensive_rebounds=Avg('offensive_rebounds'),
            avg_defensive_rebounds=Avg('defensive_rebounds'),
            avg_rebounds=Avg('total_rebounds'),
            avg_steals=Avg('steals'),
            avg_blocks=Avg('blocks'),
            avg_turnovers=Avg('turnovers'),
            avg_personal_fouls=Avg('personal_fouls'),
            avg_plus_minus=Avg('plus_minus'),
            avg_game_score=Avg('game_score'),
        )
        avg_stats['avg_minutes'] = avg_minutes
        avg_stats['games_played'] = len(game_logs)
        avg_stats['games_started'] = len(game_logs.filter(started=True))
        career_averages_gen_stats[(player_season.team.name, player_season.year)] = avg_stats

    for player_season in player_seasons:
        game_logs = GameLogPlayerAdvancedStats.objects.filter(player=player_season,team=player_season.team.abbreviation)
        minutes_played = [log.minutes_played for log in game_logs]
        avg_minutes = minutes_to_average_print(minutes_played)
        avg_stats = game_logs.aggregate(
            avg_true_shooting_percentage=Avg('true_shooting_percentage'),
            avg_effective_field_goal_percentage=Avg('effective_field_goal_percentage'),
            avg_assist_percentage=Avg('assist_percentage'),
            avg_offensive_rebound_percentage=Avg('offensive_rebound_percentage'),
            avg_defensive_rebound_percentage=Avg('defensive_rebound_percentage'),
            avg_total_rebound_percentage=Avg('total_rebound_percentage'),
            avg_steal_percentage=Avg('steal_percentage'),
            avg_block_percentage=Avg('block_percentage'),
            avg_turnover_percentage=Avg('turnover_percentage'),
            avg_usage_rate=Avg('usage_rate'),
            avg_offensive_rating=Avg('offensive_rating'),
            avg_defensive_rating=Avg('defensive_rating'),
      
        )
        avg_stats['avg_minutes'] = avg_minutes
        avg_stats['games_played'] = len(game_logs)
        avg_stats['games_started'] = len(game_logs.filter(started=True))
        career_averages_adv_stats[(player_season.team.name, player_season.year)] = avg_stats

    current_team = player.current_team
    current_player_season = player_seasons.filter(team=current_team).first()

    last_5_games_general = GameLogPlayerGeneralStats.objects.filter(player=current_player_season).order_by('-date')[:5]
    last_5_games_advanced = GameLogPlayerAdvancedStats.objects.filter(player=current_player_season).order_by('-date')[:5]
    selected_year = request.GET.get('season')
    selected_year = YEAR if selected_year is None else selected_year
    selected_team_abbr = request.GET.get('team')
    selected_team_abbr = current_team.abbreviation if selected_team_abbr is None else selected_team_abbr
    selected_team = Team.objects.prefetch_related('teamgameloggeneralstats').filter(abbreviation=selected_team_abbr).first()
    games_played = len(selected_team.teamgameloggeneralstats.filter(season=YEAR))
    selected_player_season = player_seasons.filter(year=selected_year,team=selected_team).first()

    full_season_general = GameLogPlayerGeneralStats.objects.filter(player=selected_player_season, season=selected_year,team=selected_team_abbr).order_by('-date')
    full_season_advanced = GameLogPlayerAdvancedStats.objects.filter(player=selected_player_season, season=selected_year,team=selected_team_abbr).order_by('-date')

    next_5_games = TeamSchedule.objects.filter(team=current_team,season=YEAR)[games_played:games_played+5]
    return render(request, 'player_profile.html', {
        'player': player,
        'current_team' : current_team,
        'career_averages_gen_stats': career_averages_gen_stats,
        'career_averages_adv_stats': career_averages_adv_stats,
        'last_5_games_general': last_5_games_general,
        'last_5_games_advanced': last_5_games_advanced,
        'full_season_general': full_season_general,
        'full_season_advanced': full_season_advanced,
        'player_seasons': player_seasons,
        'selected_year': selected_year,
        'next_5_games': next_5_games,
    })


def predict_player_stats(request, player_id,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold):
    starts = request.GET.get('starts', 'false') == 'true'
    stats = {
        "Points": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.POINTS),
        "Assists": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.ASSISTS),
        "Blocks": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.BLOCKS),
        "Rebounds": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.REBOUNDS),
        "Steals": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.STEALS),
        "Game_Score": get_player_stat_model(player_id,starts,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100, Stats.GAME_SCORE),
    }

    return JsonResponse({'stats':stats})

def player_estimator(request,team_id,player_id):
    player = get_object_or_404(Player, id=player_id)
    total_games_played = 0
    player_seasons_current_year = PlayerSeason.objects.prefetch_related(
        'gamelogplayergeneralstats').filter(player=player,year=YEAR)
    for player_season in player_seasons_current_year:
        total_games_played += len(player_season.gamelogplayergeneralstats.all())
    
    return render(request, 'player_estimator.html',{
        'player': player,
        'total_games_played' : total_games_played,
        'current_test_games': round(total_games_played * 0.8 )
    })

def graph_tendency(request, player_id, stat,test_size_percentage,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold):
    match(stat):
        case "Points": 
            input = Stats.POINTS
        case "Assists":
            input = Stats.ASSISTS
        case "Rebounds":
            input = Stats.REBOUNDS
        case "Steals":
            input = Stats.STEALS
        case "Blocks":
            input = Stats.BLOCKS
        case "Game Score":
            input = Stats.GAME_SCORE
    graph_player_stat(player_id,input,test_size_percentage/100,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold/100,correlation_threshold/100)
    return render(request, 'player_estimator.html')

