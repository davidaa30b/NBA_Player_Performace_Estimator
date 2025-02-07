import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from performance_estimator.constants import TEAMS, Stats
from performance_estimator.scripts.error_estimate_player_stats import graph_player_stat
from performance_estimator.utils.model_loader import ModelLoader

# Function to get weights


class Command(BaseCommand):
    help = 'Predicts players stat based on user input'

    def handle(self, *args, **kwargs):
        player_name = "LeBron James"  
        graph_player_stat(player_name,Stats.POINTS)