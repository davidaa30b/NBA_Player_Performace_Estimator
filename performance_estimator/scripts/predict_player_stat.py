from datetime import datetime
from bs4 import BeautifulSoup
from django.db.models import F
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from performance_estimator.models import Player, PlayerSeason,Team
from performance_estimator.constants import LAST_NUMBER_GAMES, TEAM_FULL_NAMES, TEAMS, YEAR,Stats
from performance_estimator.utils.model_initializer import initialize_data
from performance_estimator.utils.model_loader import ModelLoader




def get_player_stat_model(player_id:int,starts,stat:str = Stats.POINTS):
    player = Player.objects.get(id=player_id)
    
    player_seasons = PlayerSeason.objects.prefetch_related(
 
    ).filter(player=player)

    
    seasons = {season.year for season in player_seasons if season.year!=YEAR}
    X_train_data = []  
    y_train_data = []  
    for season in seasons:
        model = ModelLoader(player, season)
        df_train_model = model.model_load_data(stat)
        X, y = df_train_model.drop(columns=['date','target']), df_train_model['target']
        X_train_data.append(X)
        y_train_data.append(y)

    model_today = ModelLoader(player, YEAR)
    df_train_model_today = model_today.model_load_data(stat)
    X_today, y_today = df_train_model_today.drop(columns=['date','target']), df_train_model_today['target']
    
    X_train_data.append(X_today)
    y_train_data.append(y_today)

    X_train = pd.concat(X_train_data)
    y_train = pd.concat(y_train_data)  

    df_test_model,date,location,oppponent_full_name = model_today.model_loader_predict_data(starts)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    df_test_model = df_test_model.drop(columns=['date','target'], errors='ignore')  
    prediction = model.predict(df_test_model)
    stats = {
            'prediction': prediction[0],
            'date': date,
            'location': location,
            'opponent': oppponent_full_name
        }
    
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': importances
    })

    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
    print(player)
    print(stats)
    return stats    
