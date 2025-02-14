import numpy as np
import pandas as pd
from django.test import TestCase
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from performance_estimator.constants import ADVANCED_STATS, BROWSER_HEADERS, GENERAL_STATS, SITE_LINK, YEAR, Stats

from performance_estimator.models import GameLogPlayerGeneralStats, Team,Player,PlayerSeason, TeamGameLogGeneralStats
from performance_estimator.scripts.error_estimate_player_stats import plot_results, prepare_data_from_before_today, prepare_data_from_today, train_and_predict_data
from performance_estimator.scripts.fetch_basketball_players_data import fetch_game_data_for_player, fetch_player_game_log, fetch_roster_table, get_players_game_logs_links, save_game_data_player
from performance_estimator.scripts.fetch_basketball_teams_data import fetch_game_data_for_team, get_team_game_log_columns, get_team_table_logs, save_game_data_team
from performance_estimator.scripts.predict_player_stat import get_player_stat_model
from performance_estimator.utils.data_trainer import data_cleasing
from performance_estimator.utils.exceptions import PageCouldNotBeRetrievedError, TableNotFoundError

class PlayerGameLogTestsFetching(TestCase):
    
    def setUp(self):
        self.team = Team.objects.create(name="Lakers", abbreviation="LAL")  
        self.player = Player.objects.create(name="LeBron James")
        self.player_season = PlayerSeason.objects.create(player=self.player, team=self.team, year=YEAR)
        self.sample_html_roster = """
        <table id="roster">
            <tr><th>Player</th></tr>
            <tr>
                <td data-stat="player"><a href="/players/j/jamesle01.html">LeBron James</a></td>
            </tr>
            <tr>
                <td data-stat="player"><a href="/players/d/davisan02.html">Anthony Davis</a></td>
            </tr>
        </table>
        """
        self.soup_roster = BeautifulSoup(self.sample_html_roster, 'html.parser')
        self.columns_game_log_gen = ['Rk', 'G', 'Date', 'Age', 'Tm','Location', 'Opp','Margin','GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
        self.sample_game_log_gen = """
        <table id="game-log">
            <tr>
                <th>Rk</th>
                <th>G</th>
                <th>Date</th>
                <th>Age</th>
                <th>Tm</th>
                <th></th>
                <th>Opp</th>
                <th></th>
                <th>GS</th>
                <th>MP</th>
                <th>FG</th>
                <th>FGA</th>
                <th>FG%</th>
                <th>3P</th>
                <th>3PA</th>
                <th>3P%</th>
                <th>FT</th>
                <th>FTA</th>
                <th>FT%</th>
                <th>ORB</th>
                <th>DRB</th>
                <th>TRB</th>
                <th>AST</th>
                <th>STL</th>
                <th>BLK</th>
                <th>TOV</th>
                <th>PF</th>
                <th>PTS</th>
                <th>GmSc</th>
                <th>+/-</th>
            </tr>
            <tr>
                <th>1</th>
                <td>1</td>
                <td>2025-02-10</td>
                <td>25</td>
                <td>LAL</td>
                <td>@</td>
                <td>SAS</td>
                <td>W(+10)</td>
                <td>1</td>
                <td>36:34</td>
                <td>10</td>
                <td>20</td>
                <td>50.0</td>
                <td>2</td>
                <td>5</td>
                <td>40.0</td>
                <td>8</td>
                <td>10</td>
                <td>80.0</td>
                <td>5</td>
                <td>8</td>
                <td>13</td>
                <td>4</td>
                <td>1</td>
                <td>2</td>
                <td>3</td>
                <td>3</td>
                <td>30</td>
                <td>20</td>
                <td>+5</td>
            </tr>
            <tr>
                <th>2</th>
                <td>2</td>
                <td>2025-02-11</td>
                <td>25</td>
                <td>LAL</td>
                <td>@</td>
                <td>NYK</td>
                <td>L(-12)</td>
                <td>1</td>
                <td>30:55</td>
                <td>8</td>
                <td>18</td>
                <td>44.4</td>
                <td>3</td>
                <td>8</td>
                <td>37.5</td>
                <td>7</td>
                <td>9</td>
                <td>77.8</td>
                <td>6</td>
                <td>7</td>
                <td>13</td>
                <td>3</td>
                <td>2</td>
                <td>4</td>
                <td>4</td>
                <td>4</td>
                <td>28</td>
                <td>18</td>
                <td>+7</td>
            </tr>
        </table>
        """
        self.mock_game_data = {
            "rank": 1,
            "number": 23,
            "date": "2024-01-01",
            "age": "38",
            "team": "Lakers",
            "location": True,
            "opponent": "Celtics",
            "margin": "+10",
            "started": True,
            "minutes_played": "38",
            "field_goals": 10,
            "field_goals_attempted": 20,
            "field_goal_percentage": 50.0,
            "three_pointers": 3,
            "three_pointers_attempted": 7,
            "three_pointers_percentage": 42.9,
            "free_throws": 5,
            "free_throws_attempted": 6,
            "free_throw_percentage": 83.3,
            "offensive_rebounds": 2,
            "defensive_rebounds": 8,
            "total_rebounds": 10,
            "assists": 7,
            "steals": 2,
            "blocks": 1,
            "turnovers": 3,
            "personal_fouls": 2,
            "points": 28,
            "game_score": 25.3,
            "plus_minus": "+15"
        }

        self.mock_game_data_columns = list(self.mock_game_data.keys())

 


    @patch("time.sleep", return_value=None)  # Prevent delays during testing
    def test_get_players_game_logs_general_stats(self, _):
        """Test fetching player game log links for GENERAL_STATS"""
        log_type = GENERAL_STATS
        expected_links = [
            (f"{SITE_LINK}/players/j/jamesle01/gamelog/{YEAR}", "LeBron James"),
            (f"{SITE_LINK}/players/d/davisan02/gamelog/{YEAR}", "Anthony Davis")

        ]

        result = get_players_game_logs_links(self.soup_roster, log_type)
        self.assertEqual(result, expected_links)

    @patch("time.sleep", return_value=None)
    def test_get_players_game_logs_advanced_stats(self, _):
        """Test fetching player game log links for ADVANCED_STATS"""
        log_type = ADVANCED_STATS
        expected_links = [
            (f"{SITE_LINK}/players/j/jamesle01/gamelog-advanced/{YEAR}", "LeBron James"),
            (f"{SITE_LINK}/players/d/davisan02/gamelog-advanced/{YEAR}", "Anthony Davis"),
        ]

        result = get_players_game_logs_links(self.soup_roster, log_type)
        self.assertEqual(result, expected_links)

    def test_get_players_game_logs_no_roster(self):
        with self.assertRaises(TableNotFoundError):  
            get_players_game_logs_links(None, GENERAL_STATS)


    @patch('requests.get')
    def test_fetch_player_game_log(self, mock_get):
        player_games_log_url = "https://www.example.com/players/j/jamesle01/gamelog/2025"
        player_name = "LeBron James"
        table_type = "pgl_basic"  
        
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b"""
        <html><body>
            <table id="pgl_basic">
                <tr><th>Date</th><th>Opponent</th><th>Points</th></tr>
                <tr><td>2025-02-01</td><td>NYK/td><td>25</td></tr>
            </table>
        </body></html>
        """  
        mock_get.return_value = mock_response    
        result_table, result_response, result_player_season = fetch_player_game_log(self.team, player_games_log_url, player_name, table_type)      
        self.assertEqual(result_player_season, self.player_season)
        self.assertEqual(result_response.status_code, 200)
        self.assertIsNotNone(result_table)
        self.assertEqual(result_table.get('id'), table_type)
        mock_get.assert_called_with(player_games_log_url, headers=BROWSER_HEADERS)

    @patch('requests.get')
    def test_player_season_creation_when_not_exists(self, mock_get):
        self.player_season.delete()  
        
        player_games_log_url = "https://www.example.com/players/j/jamesle01/gamelog/2025"
        player_name = "LeBron James"
        table_type = "pgl_basic"
        
        # Mocking the response from requests.get
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b"""
        <html><body>
            <table id="pgl_basic">
                <tr><th>Date</th><th>Opponent</th><th>Points</th></tr>
                <tr><td>2025-02-01</td><td>NYK</td><td>25</td></tr>
            </table>
        </body></html>
        """ 
        mock_get.return_value = mock_response
        result_table, result_response, _ = fetch_player_game_log(self.team, player_games_log_url, player_name, table_type)
        self.assertTrue(PlayerSeason.objects.filter(player=self.player, team=self.team, year=YEAR).exists())
        self.assertEqual(result_response.status_code, 200)
        self.assertIsNotNone(result_table)
        self.assertEqual(result_table.get('id'), table_type)

    @patch('requests.get')
    def test_fetch_player_game_log_no_table(self, mock_get):
        self.player_season.delete()  
        
        player_games_log_url = "https://www.example.com/players/j/jamesle01/gamelog/2025"
        player_name = "LeBron James"
        table_type = "pgl_basic"
        
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b"""
        <html><body>
      
        </body></html>
        """ 
        mock_get.return_value = mock_response
        with self.assertRaises(TableNotFoundError):  
            fetch_player_game_log(self.team, player_games_log_url, player_name, table_type)
            
    def test_fetch_game_data_for_player_valid_data(self):
        soup = BeautifulSoup(self.sample_game_log_gen, 'html.parser')
        row = soup.find_all('tr')[1]  
        index = 0      
        game_data = fetch_game_data_for_player(self.columns_game_log_gen, row, index)
        print("gamee",game_data)
        self.assertEqual(game_data['Rk'], '1')
        self.assertEqual(game_data['G'], 1)
        self.assertEqual(game_data['Date'], '2025-02-10')
        self.assertEqual(game_data['Opp'], 'SAS')
        self.assertEqual(game_data['GS'], 1)
        self.assertEqual(game_data['MP'], '36:34')
        self.assertEqual(game_data['FG'], 10)
        self.assertEqual(game_data['FGA'], 20)
        self.assertEqual(game_data['FG%'], 50.0)
        self.assertEqual(game_data['3P'], 2)
        self.assertEqual(game_data['3PA'], 5)
        self.assertEqual(game_data['3P%'], 40.0)
        self.assertEqual(game_data['FT'], 8)
        self.assertEqual(game_data['FTA'], 10)
        self.assertEqual(game_data['FT%'], 80.0)
        self.assertEqual(game_data['Location'], False) 
        self.assertEqual(game_data['Margin'], 'W(+10)')


    @patch("performance_estimator.models.GameLogPlayerGeneralStats.save", return_value=None) 
    @patch("performance_estimator.models.GameLogPlayerGeneralStats.get_properties", return_value=["id", "field_goals", "field_goals_attempted", "field_goal_percentage", "extra"])  
    def test_save_valid_data_general_stats(self, mock_get_properties,  mock_save):

        game_data = {'field_goals': 5, 'field_goals_attempted': 10, 'field_goal_percentage': 50.0}
        columns = ['field_goals', 'field_goals_attempted', 'field_goal_percentage']

        result = save_game_data_player(GENERAL_STATS, game_data, self.player_season, columns)
        self.assertIsInstance(result, GameLogPlayerGeneralStats)
        self.assertEqual(result.player, self.player_season)
        self.assertEqual(result.field_goals, 5)
        self.assertEqual(result.field_goals_attempted, 10)
        self.assertEqual(result.field_goal_percentage, 50.0)
        mock_get_properties.assert_called_once()
        mock_save.assert_called_once()

    @patch("requests.get") 
    def test_fetch_roster_table_success(self, mock_get):
        team = Team.objects.create(name="Los Angeles Fakers", abbreviation="LAF", image="")

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b"""
        <html>
            <body>
                <table id="roster">
                    <tr><th>Player</th></tr>
                    <tr><td>Fake Player 1</td></tr>
                    <tr><td>Fake Player 2</td></tr>
                </table>
            </body>
        </html>
        """  
        mock_get.return_value = mock_response

        roster_table = fetch_roster_table(team)

        self.assertIsNotNone(roster_table)
        self.assertEqual(roster_table.name, "table")  # Ensure it's a table element
        self.assertEqual(roster_table["id"], "roster")  # Ensure it's the correct table

    @patch("requests.get")
    def test_fetch_roster_table_not_found(self, mock_get):
        team = Team.objects.create(name="Los Angeles Fakers", abbreviation="LAF", image="")

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b"""
        <html>
            <body>
                <h1>No Roster Available</h1>
            </body>
        </html>
        """  
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            fetch_roster_table(team)

        self.assertIn("Roster", str(context.exception)) 

    @patch("requests.get")
    def test_fetch_roster_table_failed_request(self, mock_get):
        team = Team.objects.create(name="Los Angeles Fakers", abbreviation="LAF", image="")
        mock_response = requests.Response()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        result = fetch_roster_table(team)
        self.assertIsNone(result)  

class TeamGameLogTestsFetching(TestCase):
    @patch('performance_estimator.scripts.fetch_basketball_teams_data.BeautifulSoup')  
    @patch('requests.get')  
    def test_get_team_table_logs_success(self, mock_get, mock_bs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
            <html>
                <table id="tgl_basic">
                    <thead>
                        <tr><th>Date</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>2025-02-12</td></tr>
                    </tbody>
                </table>
            </html>
        """
        mock_get.return_value = mock_response  

        mock_soup = MagicMock()
        
        mock_table = MagicMock()
        mock_table['id'] = 'tgl_basic' 

        mock_soup.find.return_value = mock_table  
        mock_bs.return_value = mock_soup 
        log_table = get_team_table_logs('LAL', GENERAL_STATS)
        self.assertIsNotNone(log_table)  


    @patch('performance_estimator.scripts.fetch_basketball_teams_data.BeautifulSoup') 
    @patch('requests.get')  
    def test_get_team_table_logs_failure(self, mock_bs, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(PageCouldNotBeRetrievedError):
            get_team_table_logs('LAL', GENERAL_STATS)
        
        mock_response.status_code = 200
        mock_response.text = "<html></html>"  
        mock_get.return_value = mock_response
        
        mock_soup = MagicMock()
        mock_soup.find.return_value = None  
        mock_bs.return_value = mock_soup  
        
        with self.assertRaises(TableNotFoundError):
            get_team_table_logs('LAL', GENERAL_STATS)

    @patch('requests.get')
    def test_get_team_table_logs_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with self.assertRaises(PageCouldNotBeRetrievedError):
            get_team_table_logs('LAL', GENERAL_STATS)
    
    def test_get_team_game_log_columns_general(self):
        html = '<table><thead><tr><th>''</th><th>Score</th><th>Team</th><th>Opponent</th></tr><tr><th>Rank</th><th>Game</th><th>Date</th><th>''</th><th>Opp</th><th>Rslt</th><th>Team</th><th>Opp</th></tr></thead></table>'
        soup = BeautifulSoup(html, 'html.parser')
        log_table = soup.find('table')
        columns = get_team_game_log_columns(log_table, GENERAL_STATS)
        self.assertIn('Location', columns)
        self.assertIn('Opponent Name', columns)

    def test_fetch_game_data_for_team_valid_row(self):
        html = '<tr><th>1</th><td>1</td><td>2025-02-12</td><td>@</td><td>LAL</td></tr>'
        soup = BeautifulSoup(html, 'html.parser')
        row = soup.find('tr')
        columns = ['Rank','Game', 'Date', 'Location', 'Opponent']
        game_data = fetch_game_data_for_team(columns, row, 0)
        self.assertEqual(game_data['Location'], False)  
        self.assertEqual(game_data['Game'], 1)
        self.assertEqual(game_data['Date'], '2025-02-12')
        self.assertEqual(game_data['Opponent'], 'LAL')

    def test_save_general_stats(self):
        log_type = GENERAL_STATS
        team = Team.objects.create(name="Los Angeles Fakers", abbreviation="LAF", image="")
        game_data = {
            "Rank": 5,
            "Game": 1,
            "Date": '2025-02-12', 
            "Location": False,
            "Opponent": "NYK",
            "W/L": "W",
            "Team Points": 110,
            "Opponent Points": 102,
            "Team Field Goals": 45,
            "Team Field Goals Attempted": 90,
            "Team Field Goal Percentage": 50.0,
            "Team Three Pointers": 12,
            "Team Three Pointers Attempted": 35,
            "Team Three Pointers Percentage": 34.3,
            "Team Free Throws": 18,
            "Team Free Throws Attempted": 22,
            "Team Free Throw Percentage": 81.8,
            "Team Offensive Rebounds": 10,
            "Team Total Rebounds": 45,
            "Team Assists": 25,
            "Team Steals": 8,
            "Team Blocks": 6,
            "Team Turnovers": 14,
            "Team Personal Fouls": 20,
            "Opponent Field Goals": 40,
            "Opponent Field Goals Attempted": 85,
            "Opponent Field Goal Percentage": 47.1,
            "Opponent Three Pointers": 10,
            "Opponent Three Pointers Attempted": 30,
            "Opponent Three Pointers Percentage": 33.3,
            "Opponent Free Throws": 12,
            "Opponent Free Throws Attempted": 15,
            "Opponent Free Throw Percentage": 80.0,
            "Opponent Offensive Rebounds": 8,
            "Opponent Total Rebounds": 40,
            "Opponent Assists": 20,
            "Opponent Steals": 7,
            "Opponent Blocks": 4,
            "Opponent Turnovers": 16,
            "Opponent Personal Fouls": 22
        }

        columns = [
            "Rank", "Game", "Date", "Location", "Opponent", "W/L", "Team Points", "Opponent Points",
            "Team Field Goals", "Team Field Goals Attempted", "Team Field Goal Percentage",
            "Team Three Pointers", "Team Three Pointers Attempted", "Team Three Pointers Percentage",
            "Team Free Throws", "Team Free Throws Attempted", "Team Free Throw Percentage",
            "Team Offensive Rebounds", "Team Total Rebounds", "Team Assists", "Team Steals",
            "Team Blocks", "Team Turnovers", "Team Personal Fouls",
            "Opponent Field Goals", "Opponent Field Goals Attempted", "Opponent Field Goal Percentage",
            "Opponent Three Pointers", "Opponent Three Pointers Attempted", "Opponent Three Pointers Percentage",
            "Opponent Free Throws", "Opponent Free Throws Attempted", "Opponent Free Throw Percentage",
            "Opponent Offensive Rebounds", "Opponent Total Rebounds", "Opponent Assists",
            "Opponent Steals", "Opponent Blocks", "Opponent Turnovers", "Opponent Personal Fouls"
        ]

    
        saved_stats = save_game_data_team(log_type, game_data, team, columns)
        
        self.assertEqual(saved_stats.rank, 5)
        self.assertEqual(saved_stats.number, 1)
        self.assertEqual(saved_stats.date, '2025-02-12')
        self.assertEqual(saved_stats.location, False)
        self.assertEqual(saved_stats.opponent, "NYK")

class TestDataProcessing(TestCase):
    
    @patch('performance_estimator.scripts.error_estimate_player_stats.ModelLoader')
    def test_prepare_data_from_before_today(self, MockModelLoader):
        # Arrange
        mock_model = MockModelLoader.return_value
        mock_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'opponent' : ['NYK','SAS'],
            'target': [10, 20],
            'feature1': [1.1, 2.2],
            'feature2': [3.3, 4.4]
        })
        mock_model.model_load_data.return_value = mock_df
        
        seasons = [2023, 2024]
        player = Player.objects.create(name="LeTire James")     
        stat = Stats.POINTS
        last_number_games = 5
        
        # Act
        X_train_data, y_train_data = prepare_data_from_before_today(seasons, player, stat, last_number_games)
        
        # Assert
        self.assertEqual(len(X_train_data), 2)
        self.assertEqual(len(y_train_data), 2)

    @patch('performance_estimator.scripts.error_estimate_player_stats.ModelLoader')
    def test_prepare_data_from_today(self, MockModelLoader):
        mock_model = MockModelLoader.return_value
        mock_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'target': [10, 20, 30, 40],
            'feature1': [1.1, 2.2, 3.3, 4.4],
            'feature2': [3.3, 4.4, 5.5, 6.6],
            'opponent': ['NYK', 'BOS', 'LAL', 'MIA']
        })

        assert not mock_df.empty, "Mock data should not be empty!"

       
        player = Player.objects.create(name="LeTire James")   
        stat = Stats.POINTS
        test_size_percentage = 0.5
        last_number_games = 5
        mock_model.model_load_data.return_value = mock_df
      
        
        X_train, X_test, y_train, y_test, test_game_dates, test_game_opponents = prepare_data_from_today(
            player, stat, test_size_percentage, last_number_games
        )
        
        self.assertEqual(len(X_train), 2)
        self.assertEqual(len(X_test), 2)
        self.assertEqual(len(test_game_dates), 2)
        self.assertEqual(len(test_game_opponents), 2)

    def test_train_and_predict_data(self):
        model = RandomForestRegressor()
        X_train_cleaned = pd.DataFrame({'feature1': [1, 2, 3], 'feature2': [4, 5, 6]})
        y_train = pd.Series([10, 20, 30])
        X_test_cleaned = pd.DataFrame({'feature1': [1,2], 'feature2': [4,5]})
        y_test = [40, 50]
        
        predictions = train_and_predict_data(model, X_train_cleaned, X_test_cleaned, y_test, y_train)
        
        self.assertEqual(len(predictions), 2)
        self.assertIsInstance(predictions, list)

    def test_data_cleasing(self):
        X_train = pd.DataFrame({
           'assits':[4,5,12,7],
           'rebounds':[4,5,2,7],
           'personal_fouls':[2,2,3,1],
           'three_pointers_attempted':[5,12,13,9],
           'three_pointers_made':[3,8,7,6],
                     
        })
        y_train = pd.Series([10, 22, 3, 40])
        df_test_model = pd.DataFrame({
           'assits':[6,2],
           'rebounds':[2,7],
           'personal_fouls':[4,1],
           'three_pointers_attempted':[6,10],
           'three_pointers_made':[3,5],
        })
        
        model, X_train_cleaned, df_test_cleaned = data_cleasing(
            X_train, y_train, df_test_model, 100, None, 2, 1, 'squared_error', 0.01, 0.9
        )
        self.assertIn('assits', X_train_cleaned.columns)
        self.assertIn('rebounds', X_train_cleaned.columns)
        self.assertIn('three_pointers_attempted', X_train_cleaned.columns)
        self.assertNotIn('three_pointers_made', X_train_cleaned.columns)
        self.assertNotIn('personal_fouls', X_train_cleaned.columns)


    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.text')
    @patch('matplotlib.pyplot.legend')
    @patch('matplotlib.pyplot.grid')
    @patch('matplotlib.pyplot.show')
    def test_plot_results(self, mock_show, mock_grid, mock_legend, mock_text, mock_title, mock_ylabel, mock_xlabel, mock_xticks, mock_plot):
        player = MagicMock()
        player.name = "Player1"
        stat = Stats.POINTS
        X_test = np.array([1, 2, 3])
        y_test = np.array([10, 20, 30])
        predictions = np.array([10, 19, 28])
        test_game_dates = ['2025-01-01', '2025-01-02', '2025-01-03']
        test_game_opponents = [1, 2, 3]
        X_train_today = np.array([1, 2, 3])
        X_test_today = np.array([1, 2, 3])
        last_number_games = 0

        plot_results(player, stat, X_test, y_test, X_train_today, X_test_today, test_game_dates, test_game_opponents, last_number_games, predictions)

        mock_plot.assert_called()
        mock_xticks.assert_called()
        mock_xlabel.assert_called_with(f'Game Number ({YEAR} Season)')
        mock_ylabel.assert_called_with(f'{stat}')
        mock_title.assert_called()
        mock_text.assert_called()

    






