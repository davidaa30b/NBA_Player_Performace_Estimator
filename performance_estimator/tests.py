from django.test import TestCase
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
from performance_estimator.constants import GENERAL_STATS, YEAR

from performance_estimator.models import GameLogPlayerGeneralStats, Team,Player,PlayerSeason
from performance_estimator.scripts.fetch_basketball_players_data import fetch_game_data_for_player, fetch_player_game_log, fetch_team_page, get_player_links_from_team_page, save_game_data_player

class PlayerGameLogTestsFetching(TestCase):

    def setUp(self):
        self.team = Team.objects.create(name="Lakers", abbreviation="LAL")  
        self.player = Player.objects.create(name="LeBron James")
        self.player_season = PlayerSeason.objects.create(player=self.player, team=self.team, year=YEAR)

    @patch("requests.get")
    def test_fetch_team_page_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table id='roster'></table></body></html>"
        mock_get.return_value = mock_response
        
        soup = fetch_team_page(self.team)
        
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertIsNotNone(soup.find("table", {"id": "roster"}))

    @patch("requests.get")
    def test_fetch_team_page_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        soup = fetch_team_page(self.team)
        
        self.assertIsNone(soup)

    def test_get_player_links_from_team_page(self):
        html = """
        <table id="roster">
            <tr><td data-stat="player"><a href="/players/j/jamesle01.html">LeBron James</a></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = get_player_links_from_team_page(soup, GENERAL_STATS)
        
        self.assertEqual(len(links), 1)
        self.assertIn("LeBron James", links[0])

    # @patch("requests.get")
    # def test_fetch_player_game_log_success(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.text = "<html><body><table id='pgl_basic'></table></body></html>"
    #     mock_get.return_value = mock_response

    #     soup, response, season = fetch_player_game_log(self.team, "fake_url", "LeBron James")

    #     self.assertIsInstance(soup, BeautifulSoup)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(season.player.name, "LeBron James")

    # def test_fetch_game_data_for_player(self):
    #     html = """
    #     <tr>
    #         <th>1</th>
    #         <td>Dec 25</td>
    #         <td>10</td>
    #         <td>@</td>
    #         <td>5</td>
    #     </tr>
    #     """
    #     columns = ["Rank", "Game", "Points", "Location", "Assists"]
    #     soup = BeautifulSoup(html, 'html.parser')
    #     row = soup.find("tr")
        
    #     game_data = fetch_game_data_for_player(columns, row, 1)
        
    #     self.assertEqual(game_data["Rank"], "1")
    #     self.assertEqual(game_data["Game"], "Dec 25")
    #     self.assertEqual(game_data["Points"], 10)
    #     self.assertFalse(game_data["Location"])  # @ means away (False)

    # def test_save_game_data_player(self):
    #     game_data = {
    #         "Date": "2024-02-09",
    #         "Points": 25,
    #         "Assists": 8,
    #         "Location": True,
    #     }
    #     columns = ["Date", "Points", "Assists", "Location"]

    #     save_game_data_player(GENERAL_STATS, game_data, self.player_season, columns)

    #     saved_game = GameLogPlayerGeneralStats.objects.filter(player=self.player_season, date="2024-02-09").first()

    #     self.assertIsNotNone(saved_game)
    #     self.assertEqual(saved_game.Points, 25)
    #     self.assertEqual(saved_game.Assists, 8)
    #     self.assertTrue(saved_game.Location)


