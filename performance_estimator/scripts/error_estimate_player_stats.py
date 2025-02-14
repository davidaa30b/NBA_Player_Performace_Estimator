import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from performance_estimator.constants import TEAMS, YEAR
from performance_estimator.utils.data_trainer import data_cleasing,get_weights
from performance_estimator.utils.model_loader import ModelLoader
from performance_estimator.utils.prepare_data_for_prediction import get_player_seasons



def prepare_data_from_before_today(seasons,player,stat,last_number_games):
    X_prev_train_data = []  
    y_prev_train_data = []  
    for season in seasons:
        model = ModelLoader(player, season,last_number_games)
        df_train_model = model.model_load_data(stat)
        X, y = df_train_model.drop(columns=['date','target']), df_train_model['target']
        X_prev_train_data.append(X)
        y_prev_train_data.append(y)
    return X_prev_train_data, y_prev_train_data

def prepare_data_from_today(player,stat,test_size_percentage,last_number_games):
    model_today = ModelLoader(player, YEAR,last_number_games)

    df_train_model_today = model_today.model_load_data(stat)
 
    df_train_model_today = df_train_model_today.sort_values(by='date', ascending=True)
    X_today, y_today = df_train_model_today.drop(columns=['date','target']), df_train_model_today['target']
    X_train_today, X_test_today, y_train_today, y_test_today = train_test_split(
        X_today, y_today, test_size=test_size_percentage, shuffle=False
    )
    game_dates_today = df_train_model_today["date"].values  
    game_opponents_today = df_train_model_today["opponent"].values
    test_game_dates = game_dates_today[len(X_train_today):]  
    test_game_opponents = game_opponents_today[len(X_train_today):]  
    return X_train_today, X_test_today, y_train_today, y_test_today,test_game_dates,test_game_opponents

def train_and_predict_data(model,X_train_cleaned,X_test_cleaned,y_test,y_train):
    predictions = []
    for i in range(len(X_test_cleaned)):
        weights = get_weights(y_train)

        model.fit(X_train_cleaned, y_train, sample_weight=weights)

        X_next = X_test_cleaned.iloc[i:i+1]
        y_pred = model.predict(X_next)[0]
        predictions.append(y_pred)

        X_train_cleaned = pd.concat([X_train_cleaned, X_next], ignore_index=True)
        y_train = pd.concat([y_train, pd.Series(y_test[i])], ignore_index=True)
    return predictions

def plot_results(player,stat,X_test,y_test,X_train_today,X_test_today,test_game_dates,test_game_opponents,last_number_games,predictions):
    start_game = 0
    end_game = len(X_test)
    displayed_games = range(start_game, end_game)
    actual_values_display = y_test[start_game:end_game]
    predictions_display = predictions[start_game:end_game]

    mse = mean_squared_error(actual_values_display, predictions_display)
    rmse = np.sqrt(mse)
    error_percentages = np.abs((np.array(predictions_display) - actual_values_display) / actual_values_display) * 100
    min_error, max_error, avg_error = np.nanmin(error_percentages), np.nanmax(error_percentages), np.nanmean(error_percentages)

    plt.figure(figsize=(10, 6))
    plt.plot(displayed_games, actual_values_display, label=f'Actual {stat}', marker='o', color='blue')
    plt.plot(displayed_games, predictions_display, label=f'Predicted {stat}', marker='x', color='red')
    x_labels = [f"{date} vs {TEAMS[opp]}" for date, opp in zip(test_game_dates[start_game:end_game], test_game_opponents[start_game:end_game])]

    plt.xticks(ticks=displayed_games, labels=x_labels, rotation=45, ha="right")

    plt.xlabel(f'Game Number ({YEAR} Season)')
    plt.ylabel(f'{stat}')
    plt.title(f'{player.name}\nActual vs Predicted {stat} (Games {len(X_train_today)+last_number_games} - {len(X_train_today)+len(X_test_today)+last_number_games} of {YEAR})')

    plt.text(
        1.01, 0, 
        f'MSE: {mse:.2f}\nRMSE: {rmse:.2f}\n\nMin Error: {min_error:.2f}%\nMax Error: {max_error:.2f}%\nAvg Error: {avg_error:.2f}%', 
        horizontalalignment='left', verticalalignment='center',
        transform=plt.gca().transAxes, fontsize=8, color='black', weight='bold',
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5')
    )

    plt.legend()
    plt.grid(True)
    plt.show()

def graph_player_stat(player_id:int,stat,test_size_percentage,last_number_games,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold):
    player, seasons = get_player_seasons(player_id)
    X_prev_train_data ,y_prev_train_data = prepare_data_from_before_today(seasons,player,stat,last_number_games)
    X_train_today, X_test_today, y_train_today, y_test_today,test_game_dates,test_game_opponents = prepare_data_from_today(player,stat,test_size_percentage,last_number_games) 

    X_test = X_test_today.reset_index(drop=True)
    y_test = y_test_today.reset_index(drop=True).values
    if X_prev_train_data:
        X_prev_data = pd.concat(X_prev_train_data, ignore_index=True)
        y_prev_data = pd.concat(y_prev_train_data, ignore_index=True)
        
        X_train = pd.concat([X_prev_data, X_train_today], ignore_index=True)
        y_train = pd.concat([y_prev_data, y_train_today], ignore_index=True)
    else:
        X_train = X_train_today.copy()
        y_train = y_train_today.copy()

    model, X_train_cleaned, X_test_cleaned = data_cleasing(X_train, y_train, X_test,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold)
 
    predictions = train_and_predict_data(model,X_train_cleaned,X_test_cleaned,y_test,y_train)
    plot_results(player,stat,X_test,y_test,X_train_today,X_test_today,test_game_dates,test_game_opponents,last_number_games,predictions)
