from datetime import datetime
from bs4 import BeautifulSoup
from django.db.models import F
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from performance_estimator.models import Player, PlayerSeason,Team
from performance_estimator.constants import YEAR,Stats
from performance_estimator.utils.data_trainer import data_cleasing, get_weights
from performance_estimator.utils.model_loader import ModelLoader




def get_player_stat_model(player_id:int,starts,last_number_games:int,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold,stat:str = Stats.POINTS):
    player = Player.objects.get(id=player_id)
    
    player_seasons = PlayerSeason.objects.prefetch_related(
 
    ).filter(player=player)

    
    seasons = {season.year for season in player_seasons if season.year<YEAR}
    X_train_data = []  
    y_train_data = []  
    for season in seasons:
        model = ModelLoader(player, season,last_number_games)
        df_train_model = model.model_load_data(stat)
        X, y = df_train_model.drop(columns=['date','target']), df_train_model['target']
        X_train_data.append(X)
        y_train_data.append(y)

    model_today = ModelLoader(player, YEAR,last_number_games)
    df_train_model_today = model_today.model_load_data(stat)
    X_today, y_today = df_train_model_today.drop(columns=['date','target']), df_train_model_today['target']
    
    X_train_data.append(X_today)
    y_train_data.append(y_today)

    X_train = pd.concat(X_train_data)
    y_train = pd.concat(y_train_data)  

    df_test_model,date,location,oppponent_full_name = model_today.model_loader_predict_data(starts)

    model, cleasened_X_train,cleasened_test_model = data_cleasing(X_train,y_train,df_test_model,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold)
    weights = get_weights(y_train)

    model.fit(cleasened_X_train, y_train,sample_weight=weights)

    cleasened_test_model = cleasened_test_model.drop(columns=['date','target'], errors='ignore')  
    prediction = model.predict(cleasened_test_model)
    stats = {
            'prediction': prediction[0],
            'date': date,
            'location': location,
            'opponent': oppponent_full_name
        }
    tree_depths = [tree.get_depth() for tree in model.estimators_]
    min_depth = np.min(tree_depths)
    max_depth = np.max(tree_depths)
    print(f"Min Depth: {min_depth}, Max Depth: {max_depth}")
    
    return stats    
