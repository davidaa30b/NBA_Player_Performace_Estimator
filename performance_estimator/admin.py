from django.contrib import admin
from .models import PlayerSeason, Team, Player, GameLogPlayerGeneralStats, GameLogPlayerAdvancedStats,TeamGameLogAdvancedStats,TeamGameLogGeneralStats, TeamSchedule

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(PlayerSeason)
admin.site.register(GameLogPlayerGeneralStats)
admin.site.register(GameLogPlayerAdvancedStats)
admin.site.register(TeamGameLogAdvancedStats)
admin.site.register(TeamGameLogGeneralStats)
admin.site.register(TeamSchedule)
