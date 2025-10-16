"""
NBA Fantasy Data Collector
Scrapes player statistics, injury data, and team information
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Try importing basketball_reference_web_scraper
try:
    from basketball_reference_web_scraper import client
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("Warning: basketball_reference_web_scraper not available. Will use alternative methods.")


class NBADataCollector:
    """Collects and processes NBA data for fantasy basketball analysis"""
    
    def __init__(self, seasons=[2022, 2023, 2024, 2025], weights=None):
        """
        Args:
            seasons: List of season end years to collect (e.g., 2025 = 2024-25 season)
            weights: Dict of season weights for recency bias (e.g., {2025: 0.4, 2024: 0.3, ...})
        """
        self.seasons = seasons
        self.weights = weights or {2025: 0.40, 2024: 0.30, 2023: 0.20, 2022: 0.10}
        self.yahoo_scoring = {
            'points_scored': 1.0,
            'rebounds': 1.2,
            'assists': 1.5,
            'steals': 3.0,
            'blocks': 3.0,
            'turnovers': -1.0
        }
        
    def calculate_yahoo_fantasy_points(self, row):
        """Calculate fantasy points using Yahoo scoring"""
        try:
            total_rebounds = row.get('offensive_rebounds', 0) + row.get('defensive_rebounds', 0)
            
            fp = (
                row.get('points_scored', 0) * self.yahoo_scoring['points_scored'] +
                total_rebounds * self.yahoo_scoring['rebounds'] +
                row.get('assists', 0) * self.yahoo_scoring['assists'] +
                row.get('steals', 0) * self.yahoo_scoring['steals'] +
                row.get('blocks', 0) * self.yahoo_scoring['blocks'] +
                row.get('turnovers', 0) * self.yahoo_scoring['turnovers']
            )
            return fp
        except Exception as e:
            print(f"Error calculating fantasy points: {e}")
            return 0
    
    def get_player_game_logs(self, season_end_year):
        """
        Collect player game logs for a season
        """
        print(f"\nCollecting game logs for {season_end_year-1}-{season_end_year} season...")
        
        if not SCRAPER_AVAILABLE:
            print("Scraper not available - using backup method")
            return self._get_game_logs_backup(season_end_year)
        
        all_games = []
        
        try:
            # Get list of all players for the season
            players = client.players_season_totals(season_end_year=season_end_year)
            players_df = pd.DataFrame(players)
            
            print(f"Found {len(players_df)} players. Collecting game logs...")
            
            for idx, player in tqdm(players_df.iterrows(), total=len(players_df)):
                try:
                    slug = player['slug']
                    name = player['name']
                    
                    # Get player's game log
                    games = client.regular_season_player_box_scores(
                        player_identifier=slug,
                        season_end_year=season_end_year
                    )
                    
                    if games:
                        games_df = pd.DataFrame(games)
                        games_df['player_name'] = name
                        games_df['player_slug'] = slug
                        games_df['season_end_year'] = season_end_year
                        all_games.append(games_df)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    if idx % 50 == 0:
                        print(f"Error with player {name}: {e}")
                    continue
            
            if all_games:
                combined = pd.concat(all_games, ignore_index=True)
                combined['fantasy_points'] = combined.apply(self.calculate_yahoo_fantasy_points, axis=1)
                return combined
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error collecting game logs: {e}")
            return pd.DataFrame()
    
    def _get_game_logs_backup(self, season_end_year):
        """
        Backup method using direct Basketball-Reference scraping
        This is a placeholder - you may need to implement based on current BR structure
        """
        print("Using backup scraping method...")
        # For now, return empty DataFrame - we'll implement if needed
        return pd.DataFrame()
    
    def get_injury_data(self):
        """
        Scrape injury history from RotoWire
        Returns DataFrame with player injury information
        """
        print("\nCollecting injury data from RotoWire...")
        
        try:
            url = "https://www.rotowire.com/basketball/injury-report.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse current injury report
            injuries = []
            # This is a simplified parser - may need adjustment based on current site structure
            injury_table = soup.find('div', {'class': 'injury-report'})
            
            if injury_table:
                print("Found injury data")
                # Parse and structure the data
                # Implementation depends on current RotoWire structure
            
            # For historical injury data, we'll need to supplement from other sources
            # This is a complex task that may require multiple data sources
            
            return pd.DataFrame(injuries)
            
        except Exception as e:
            print(f"Error collecting injury data: {e}")
            return pd.DataFrame()
    
    def get_team_standings(self, season_end_year):
        """
        Get team standings to identify tanking teams vs contenders
        """
        print(f"\nGetting team standings for {season_end_year}...")
        
        try:
            # Use Basketball-Reference for standings
            url = f"https://www.basketball-reference.com/leagues/NBA_{season_end_year}_standings.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Parse Eastern and Western conference standings
            standings = pd.read_html(response.text)
            
            # Combine conferences
            east = standings[0]
            west = standings[1]
            
            # Add conference labels
            east['Conference'] = 'East'
            west['Conference'] = 'West'
            
            all_standings = pd.concat([east, west], ignore_index=True)
            all_standings['season_end_year'] = season_end_year
            
            # Calculate contender score (top 6 in conference = playoff team)
            all_standings['is_contender'] = all_standings.groupby('Conference').cumcount() < 6
            
            return all_standings
            
        except Exception as e:
            print(f"Error getting standings: {e}")
            return pd.DataFrame()
    
    def collect_all_data(self):
        """
        Main method to collect all required data
        Returns dict of DataFrames
        """
        data = {
            'game_logs': [],
            'injury_data': None,
            'standings': []
        }
        
        # Collect game logs for each season
        for season in self.seasons:
            game_logs = self.get_player_game_logs(season)
            if not game_logs.empty:
                game_logs['season_weight'] = self.weights.get(season, 0.25)
                data['game_logs'].append(game_logs)
            
            # Get standings
            standings = self.get_team_standings(season)
            if not standings.empty:
                data['standings'].append(standings)
            
            time.sleep(1)  # Be nice to servers
        
        # Combine all game logs
        if data['game_logs']:
            data['game_logs'] = pd.concat(data['game_logs'], ignore_index=True)
        else:
            data['game_logs'] = pd.DataFrame()
        
        # Combine standings
        if data['standings']:
            data['standings'] = pd.concat(data['standings'], ignore_index=True)
        else:
            data['standings'] = pd.DataFrame()
        
        # Get injury data (current season focus)
        data['injury_data'] = self.get_injury_data()
        
        return data
    
    def save_data(self, data, output_dir='data'):
        """Save collected data to disk"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if not data['game_logs'].empty:
            data['game_logs'].to_parquet(f'{output_dir}/game_logs.parquet', index=False)
            print(f"Saved game logs: {len(data['game_logs'])} records")
        
        if not data['standings'].empty:
            data['standings'].to_csv(f'{output_dir}/standings.csv', index=False)
            print(f"Saved standings: {len(data['standings'])} records")
        
        if data['injury_data'] is not None and not data['injury_data'].empty:
            data['injury_data'].to_csv(f'{output_dir}/injury_data.csv', index=False)
            print(f"Saved injury data: {len(data['injury_data'])} records")
        
        print(f"\nAll data saved to {output_dir}/")


if __name__ == "__main__":
    # Test the collector
    collector = NBADataCollector(seasons=[2024, 2025])
    data = collector.collect_all_data()
    collector.save_data(data)