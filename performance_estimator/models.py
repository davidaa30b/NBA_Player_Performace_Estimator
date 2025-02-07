from django.db import models

from performance_estimator.constants import YEAR

class Team(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)
    image = models.CharField(max_length=500,default="")
    def __str__(self):
        return self.name

class TeamSchedule(models.Model):
    date = models.DateField()
    location = models.BooleanField(default=True) 
    opponent = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name = "teamschedule")
    season = models.IntegerField(default=YEAR)
    @classmethod
    def get_properties(cls):
        return [field.name for field in cls._meta.fields]
    def __str__(self):
        return f"{self.team.name} vs {self.opponent} - {self.date}"

class TeamLogBase(models.Model):
    rank = models.IntegerField()
    number = models.IntegerField()
    date = models.DateField()
    location = models.BooleanField(default=True)
    opponent = models.CharField(max_length=100)
    win_loss_result = models.CharField(max_length=2)
    team_points = models.IntegerField()
    opponents_points = models.IntegerField()
    class Meta:
        abstract = True

    @classmethod
    def get_properties(cls):
        return [field.name for field in cls._meta.fields]

    @classmethod
    def get_field_names_by_type(cls, field_type):    
        return [field.name for field in cls._meta.fields if isinstance(field, field_type)]

    @classmethod
    def get_float_fields(cls):
        return cls.get_field_names_by_type(models.FloatField)

    @classmethod
    def get_int_fields(cls):
        return cls.get_field_names_by_type(models.IntegerField)
    
    def __str__(self):
        return f"{self.team} vs {self.opponent} - {self.date}"


class TeamGameLogGeneralStats(TeamLogBase):
    team_field_goals = models.IntegerField()
    team_field_goals_attempted = models.IntegerField()
    team_field_goal_percentage = models.FloatField()
    team_three_pointers = models.IntegerField()
    team_three_pointers_attempted = models.IntegerField()
    team_three_pointers_percentage = models.FloatField()
    team_free_throws = models.IntegerField()
    team_free_throws_attempted = models.IntegerField()
    team_free_throw_percentage = models.FloatField()
    team_offensive_rebounds = models.IntegerField()
    team_total_rebounds = models.IntegerField()
    team_assists = models.IntegerField()
    team_steals = models.IntegerField()
    team_blocks = models.IntegerField()
    team_turnovers = models.IntegerField()
    team_personal_fouls = models.IntegerField()
    opponent_field_goals = models.IntegerField()
    opponent_field_goals_attempted = models.IntegerField()
    opponent_field_goal_percentage = models.FloatField()
    opponent_three_pointers = models.IntegerField()
    opponent_three_pointers_attempted = models.IntegerField()
    opponent_three_pointers_percentage = models.FloatField()
    opponent_free_throws = models.IntegerField()
    opponent_free_throws_attempted = models.IntegerField()
    opponent_free_throw_percentage = models.FloatField()
    opponent_offensive_rebounds = models.IntegerField()
    opponent_total_rebounds = models.IntegerField()
    opponent_assists = models.IntegerField()
    opponent_steals = models.IntegerField()
    opponent_blocks = models.IntegerField()
    opponent_turnovers = models.IntegerField()
    opponent_personal_fouls = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name = "teamgameloggeneralstats")
    season = models.IntegerField(default=YEAR)


class TeamGameLogAdvancedStats(TeamLogBase):
    offensive_rating = models.FloatField()
    defensive_rating = models.FloatField()
    pace = models.FloatField()
    free_throw_attempt_rate = models.FloatField()
    three_point_attempt_rate = models.FloatField()
    true_shooting_percentage = models.FloatField()
    total_reboound_percentage = models.FloatField()
    assist_percentage = models.FloatField()
    steal_percentage = models.FloatField()
    block_percentage = models.FloatField()
    offensive_effective_field_goal_percentage = models.FloatField()
    offensive_turnover_percentage = models.FloatField()
    offensive_rebound_percentage = models.FloatField()
    offensive_free_throws_per_field_goal_attempt_percentage = models.FloatField()
    defensive_effective_field_goal_percentage = models.FloatField()
    defensive_turnover_percentage = models.FloatField()
    defensive_rebound_percentage = models.FloatField()
    defensive_free_throws_per_field_goal_attempt_percentage = models.FloatField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name = "teamgamelogadvancedstats")
    season = models.IntegerField(default=YEAR)


class Player(models.Model):
    name = models.CharField(max_length=100)
    teams = models.ManyToManyField(Team, through='playerseason')
    image = models.CharField(max_length=500,default="")
    current_team = models.ForeignKey('Team', null=True, blank=True, on_delete=models.SET_NULL, related_name="current_players")

    def __str__(self):
        return self.name

class PlayerSeason(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} - {self.team.name} ({self.year})"

class GameLogBase(models.Model):
    rank = models.IntegerField()
    number = models.IntegerField()
    date = models.DateField()
    age = models.CharField(max_length=12)
    team = models.CharField(max_length=100)
    location = models.BooleanField(default=True) 
    opponent = models.CharField(max_length=100)
    margin = models.CharField(max_length=50)
    started = models.BooleanField()
    minutes_played = models.CharField(max_length=50)

    class Meta:
        abstract = True

    @classmethod
    def get_properties(cls):
        return [field.name for field in cls._meta.fields]

    @classmethod
    def get_field_names_by_type(cls, field_type):    
        return [field.name for field in cls._meta.fields if isinstance(field, field_type)]

    @classmethod
    def get_float_fields(cls):
        return cls.get_field_names_by_type(models.FloatField)

    @classmethod
    def get_int_fields(cls):
        return cls.get_field_names_by_type(models.IntegerField)

    def __str__(self):
        return f"{self.player.player.name} - {self.date}"

class GameLogPlayerGeneralStats(GameLogBase):
    field_goals = models.IntegerField()
    field_goals_attempted = models.IntegerField()
    field_goal_percentage = models.FloatField()
    three_pointers = models.IntegerField()
    three_pointers_attempted = models.IntegerField()
    three_pointers_percentage = models.FloatField()
    free_throws = models.IntegerField()
    free_throws_attempted = models.IntegerField()
    free_throw_percentage = models.FloatField()
    offensive_rebounds = models.IntegerField()
    defensive_rebounds = models.IntegerField()
    total_rebounds = models.IntegerField()
    assists = models.IntegerField()
    steals = models.IntegerField()
    blocks = models.IntegerField()
    turnovers = models.IntegerField()
    personal_fouls = models.IntegerField()
    points = models.IntegerField()
    game_score = models.FloatField()
    plus_minus = models.CharField(max_length=50)
    player = models.ForeignKey(PlayerSeason, on_delete=models.CASCADE,related_name = "gamelogplayergeneralstats")
    season = models.IntegerField(default=YEAR)

class GameLogPlayerAdvancedStats(GameLogBase):
    true_shooting_percentage = models.FloatField()
    effective_field_goal_percentage = models.FloatField()
    offensive_rebound_percentage = models.FloatField()
    defensive_rebound_percentage = models.FloatField()
    total_rebound_percentage = models.FloatField()
    assist_percentage = models.FloatField()
    steal_percentage = models.FloatField()
    block_percentage = models.FloatField()
    turnover_percentage = models.FloatField()
    usage_rate = models.FloatField()
    offensive_rating = models.FloatField()
    defensive_rating = models.FloatField()
    game_score = models.FloatField()
    plus_minus = models.CharField(max_length=50)
    player = models.ForeignKey(PlayerSeason, on_delete=models.CASCADE,related_name = "gamelogplayeradvancedstats")
    season = models.IntegerField(default=YEAR)
