from django.db.models import F
import pandas as pd
from performance_estimator.constants import YEAR,Stats
from performance_estimator.scripts.error_estimate_player_stats import prepare_data_from_before_today
from performance_estimator.utils.data_trainer import data_cleasing, get_weights
from performance_estimator.utils.model_loader import ModelLoader
from performance_estimator.utils.prepare_data_for_prediction import get_player_seasons

def get_player_stat_model(player_id:int,starts,last_number_games:int = 5,n_trees_forest = 100,max_depth_tree =21,min_samples_split = 2,min_samples_leaf = 1,criterion='square_error',variance_threshold = 0.1,correlation_threshold = 0.9,stat:str = Stats.POINTS):
    player, seasons = get_player_seasons(player_id)

    X_train_data, y_train_data = prepare_data_from_before_today(seasons,player,stat,last_number_games)
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
    return stats    


