from django.urls import path
from .views import team_list,team_profile,predict_player_stats,graph_tendency,player_profile,player_estimator

urlpatterns = [
    path('', team_list, name='home'),
    path('teams/', team_list, name='team_list'), 
    path('teams/<int:team_id>/', team_profile, name='team_profile'), 
    path('teams/<int:team_id>/<int:player_id>/', player_profile, name='player_profile'),
    path('teams/<int:team_id>/<int:player_id>/estimator', player_estimator, name='player_estimator'), 
    path('predict_stats/<int:player_id>/<int:last_number_games>/<int:n_trees_forest>/<int:max_depth_tree>/<int:min_samples_split>/<int:min_samples_leaf>/<str:criterion>/<int:variance_threshold>/<int:correlation_threshold>/', predict_player_stats, name='predict_player_stats'),  
    path('graph_tendency/<int:player_id>/<str:stat>/<int:test_size_percentage>/<int:last_number_games>/<int:n_trees_forest>/<int:max_depth_tree>/<int:min_samples_split>/<int:min_samples_leaf>/<str:criterion>/<int:variance_threshold>/<int:correlation_threshold>/', graph_tendency, name='graph_tendency'),

]
