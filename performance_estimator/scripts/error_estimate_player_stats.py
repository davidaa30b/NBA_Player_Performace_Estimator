import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from performance_estimator.constants import TEAMS, Stats
from performance_estimator.utils.model_loader import ModelLoader


def get_weights(y_train):
    n = len(y_train)
    weights = np.linspace(0.5, 10, n)  # Linearly increasing weights
    return weights

def graph_player_stat(player_name,stat):
    model2023 = ModelLoader(player_name, 2023)
    model2024 = ModelLoader(player_name, 2024)
    model2025 = ModelLoader(player_name, 2025)

    df_train_model2023 = model2023.model_load_data(stat)
    df_train_model2024 = model2024.model_load_data(stat)
    df_train_model2025 = model2025.model_load_data(stat)

    X2023, y2023 = df_train_model2023.drop(columns=['date','target']), df_train_model2023['target']
    X2024, y2024 = df_train_model2024.drop(columns=['date','target']), df_train_model2024['target']
    X2025, y2025 = df_train_model2025.drop(columns=['date','target']), df_train_model2025['target']

    X_full = pd.concat([X2023, X2024], ignore_index=True)
    y_full = pd.concat([y2023, y2024], ignore_index=True)

    X_train_2025, X_test_2025, y_train_2025, y_test_2025 = train_test_split(
        X2025, y2025, test_size=0.8, shuffle=False
    )

    X_train = pd.concat([X_full, X_train_2025], ignore_index=True)
    y_train = pd.concat([y_full, y_train_2025], ignore_index=True)

    X_test = X_test_2025.reset_index(drop=True)
    y_test = y_test_2025.reset_index(drop=True).values

    predictions = []



    # Ensure range is within valid limits
    start_game = 0
    end_game = len(X_test)

    game_dates_2025 = df_train_model2025["date"].values  
    game_opponents_2025 = df_train_model2025["opponent"].values  

    test_game_dates = game_dates_2025[len(X_train_2025):]  
    test_game_opponents = game_opponents_2025[len(X_train_2025):]  

    # Generate x_labels for the specific range of games you're displaying
    x_labels = [f"{date} vs {TEAMS[opp]}" for date, opp in zip(test_game_dates[start_game:end_game], test_game_opponents[start_game:end_game])]
    
    # Start progressive training loop
    for i in range(len(X_test)):
        weights = get_weights(y_train)

        # Train model
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train, sample_weight=weights)

        # Predict next game
        X_next = X_test.iloc[i:i+1]
        y_pred = model.predict(X_next)[0]
        predictions.append(y_pred)

        # Add predicted game to training set
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
    plt.xlabel('Game Number (2025 Season)')
    plt.ylabel(f'{stat}')
    plt.title(f'{player_name}\nActual vs Predicted {stat} (Games {len(X_train_2025)} - {len(X_train_2025) + len(X_test_2025)} of 2025)')

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
