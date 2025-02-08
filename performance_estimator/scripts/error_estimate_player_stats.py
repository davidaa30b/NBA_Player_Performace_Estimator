import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from performance_estimator.constants import LAST_NUMBER_GAMES, TEAMS, YEAR
from performance_estimator.models import Player, PlayerSeason
from performance_estimator.utils.model_loader import ModelLoader


def get_weights(y_train):
    n = len(y_train)
    weights = np.linspace(0.5, 10, n) 
    return weights

def graph_player_stat(player_id:int,stat,test_size_percentage,last_number_games):
    print("Test size percentage!!",test_size_percentage)
    player = Player.objects.get(id=player_id)
    player_seasons = PlayerSeason.objects.prefetch_related(
 
    ).filter(player=player)

    
    seasons = {season.year for season in player_seasons if season.year<YEAR}
    X_prev_train_data = []  
    y_prev_train_data = []  
    for season in seasons:
        model = ModelLoader(player, season,last_number_games)
        df_train_model = model.model_load_data(stat)
        X, y = df_train_model.drop(columns=['date','target']), df_train_model['target']
        X_prev_train_data.append(X)
        y_prev_train_data.append(y)

    model_today = ModelLoader(player, YEAR,last_number_games)

  
    df_train_model_today = model_today.model_load_data(stat)
    df_train_model_today = df_train_model_today.sort_values(by='date', ascending=True)


    X_today, y_today = df_train_model_today.drop(columns=['date','target']), df_train_model_today['target']

    X_train_today, X_test_today, y_train_today, y_test_today = train_test_split(
        X_today, y_today, test_size=test_size_percentage, shuffle=False
    )

    X_test = X_test_today.reset_index(drop=True)
    y_test = y_test_today.reset_index(drop=True).values

    predictions = []

    start_game = 0
    end_game = len(X_test)

    game_dates_2025 = df_train_model_today["date"].values  
    game_opponents_2025 = df_train_model_today["opponent"].values  

    test_game_dates = game_dates_2025[len(X_train_today):]  
    test_game_opponents = game_opponents_2025[len(X_train_today):]  

    x_labels = [f"{date} vs {TEAMS[opp]}" for date, opp in zip(test_game_dates[start_game:end_game], test_game_opponents[start_game:end_game])]
    

    if X_prev_train_data:
        X_prev_data = pd.concat(X_prev_train_data, ignore_index=True)
        y_prev_data = pd.concat(y_prev_train_data, ignore_index=True)
        
        X_train = pd.concat([X_prev_data, X_train_today], ignore_index=True)
        y_train = pd.concat([y_prev_data, y_train_today], ignore_index=True)
    else:
        X_train = X_train_today.copy()
        y_train = y_train_today.copy()

    for i in range(len(X_test)):
        weights = get_weights(y_train)

        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train, sample_weight=weights)

        X_next = X_test.iloc[i:i+1]
        y_pred = model.predict(X_next)[0]
        predictions.append(y_pred)

        X_train = pd.concat([X_train, X_next], ignore_index=True)
        y_train = pd.concat([y_train, pd.Series(y_test[i])], ignore_index=True)

    # Select only the specified range for display
    displayed_games = range(start_game, end_game)
    actual_values_display = y_test[start_game:end_game]
    predictions_display = predictions[start_game:end_game]

    # Error calculation
    mse = mean_squared_error(actual_values_display, predictions_display)
    rmse = np.sqrt(mse)
    error_percentages = np.abs((np.array(predictions_display) - actual_values_display) / actual_values_display) * 100
    min_error, max_error, avg_error = np.nanmin(error_percentages), np.nanmax(error_percentages), np.nanmean(error_percentages)

    # Plot actual vs predicted points
    plt.figure(figsize=(10, 6))
    plt.plot(displayed_games, actual_values_display, label='Actual Points', marker='o', color='blue')
    plt.plot(displayed_games, predictions_display, label='Predicted Points', marker='x', color='red')
    
    # Set custom x-ticks with game dates and opponents
    plt.xticks(ticks=displayed_games, labels=x_labels, rotation=45, ha="right")

    # Labels and title
    plt.xlabel(f'Game Number ({YEAR} Season)')
    plt.ylabel(f'{stat}')
    plt.title(f'{player.name}\nActual vs Predicted {stat} (Games {len(X_train_today)+LAST_NUMBER_GAMES} - {len(X_today)+LAST_NUMBER_GAMES} of {YEAR})')

    # Display error metrics
    plt.text(
        1.01, 0, 
        f'MSE: {mse:.2f}\nRMSE: {rmse:.2f}\n\nMin Error: {min_error:.2f}%\nMax Error: {max_error:.2f}%\nAvg Error: {avg_error:.2f}%', 
        horizontalalignment='left', verticalalignment='center',
        transform=plt.gca().transAxes, fontsize=8, color='black', weight='bold',
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5')
    )

    plt.legend()
    plt.grid(True)

    # Show plot
    plt.show()
