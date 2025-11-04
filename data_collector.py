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
    
    def __init__(self, seasons=[2024, 2025], weights=None):
        """
        Args:
            seasons: List of season end years to collect (e.g., 2025 = 2024-25 season)
            weights: Dict of season weights for recency bias (e.g., {2025: 0.4, 2024: 0.3, ...})
        """
        self.seasons = seasons
        self.weights = weights or {2025: 0.60, 2024: 0.40}
        self.yahoo_scoring = {
            'points_scored': 1.0,
            'rebounds': 1.0,
            'assists': 2.0,
            'steals': 3.0,
            'blocks': 3.0,
            'turnovers': -1.0
        }
        # Rate limiting: 20 requests/min = 3 seconds per request minimum
        self.min_request_interval = 3.5  # 3.5 seconds to be safe
        self.last_request_time = 0
        
    def _rate_limit_sleep(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        
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
        Collect player game logs for a season with smart rate limiting
        20 requests/minute = 1 request every 3 seconds
        """
        print(f"\nCollecting game logs for {season_end_year-1}-{season_end_year} season...")
        
        if not SCRAPER_AVAILABLE:
            print("Scraper not available - using backup method")
            return self._get_game_logs_backup(season_end_year)
        
        all_games = []
        failed_players = []
        
        try:
            # Get list of all players for the season
            print("Fetching player list...")
            self._rate_limit_sleep()
            players = client.players_season_totals(season_end_year=season_end_year)
            players_df = pd.DataFrame(players)
            
            print(f"Found {len(players_df)} players. Collecting game logs...")
            print(f"⏱ Estimated time: {(len(players_df) * self.min_request_interval) / 60:.1f} minutes")
            print(f"⚠️  Rate limit: {self.min_request_interval}s between requests to respect 20 req/min limit\n")
            
            # Track requests per minute
            request_count = 0
            minute_start = time.time()
            
            for idx, player in tqdm(players_df.iterrows(), total=len(players_df), desc="Collecting"):
                try:
                    slug = player['slug']
                    name = player['name']
                    
                    # Smart rate limiting with minute-based tracking
                    request_count += 1
                    
                    # If we've made 18 requests in this minute, wait for the minute to expire
                    if request_count >= 18:
                        elapsed_in_minute = time.time() - minute_start
                        if elapsed_in_minute < 60:
                            wait_time = 62 - elapsed_in_minute  # Wait 62s to be safe
                            print(f"\n⏸  Made 18 requests. Waiting {wait_time:.0f}s for rate limit reset...")
                            time.sleep(wait_time)
                        # Reset counter
                        request_count = 0
                        minute_start = time.time()
                    
                    # Base rate limiting (3.5s between requests)
                    self._rate_limit_sleep()
                    
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
                    
                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str or 'Too Many Requests' in error_str:
                        print(f"\n⚠️  Rate limited at player #{idx+1}. Waiting 2 minutes...")
                        time.sleep(120)  # Wait 2 minutes
                        failed_players.append((idx, player))
                        # Reset counters
                        request_count = 0
                        minute_start = time.time()
                    else:
                        if idx % 100 == 0 and idx > 0:
                            print(f"\n❌ Error with {name}: {e}")
                        failed_players.append((idx, player))
                    continue
            
            # Retry failed players with longer delays
            if failed_players and len(failed_players) < 50:  # Only retry if not too many failures
                print(f"\n\n🔄 Retrying {len(failed_players)} failed players with longer delays...")
                time.sleep(30)  # Initial wait before retries
                
                for idx, player in tqdm(failed_players, desc="Retrying"):
                    try:
                        slug = player['slug']
                        name = player['name']
                        
                        time.sleep(5)  # Extra cautious delay for retries
                        
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
                        
                    except Exception as e:
                        if '429' in str(e):
                            print(f"\n⚠️  Still rate limited. Stopping retries.")
                            break
                        continue
            
            if all_games:
                combined = pd.concat(all_games, ignore_index=True)
                combined['fantasy_points'] = combined.apply(self.calculate_yahoo_fantasy_points, axis=1)
                print(f"\n✅ Successfully collected {len(combined)} games from {len(all_games)} players")
                if failed_players:
                    print(f"⚠️  Failed to collect data for {len(failed_players)} players")
                return combined
            else:
                print("\n❌ No game data collected")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"\n❌ Error collecting game logs: {e}")
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
            
            time.sleep(2)  # Rate limit for external sites too
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
            
            self._rate_limit_sleep()  # Apply rate limiting here too
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
            
            print(f"✅ Retrieved standings for {len(all_standings)} teams")
            return all_standings
            
        except Exception as e:
            print(f"❌ Error getting standings: {e}")
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
        
        print("\n" + "="*80)
        print("  NBA DATA COLLECTION STARTING")
        print("="*80)
        print(f"Seasons to collect: {self.seasons}")
        print(f"Rate limit: {self.min_request_interval}s between requests")
        print("="*80 + "\n")
        
        # Collect game logs for each season
        for i, season in enumerate(self.seasons, 1):
            print(f"\n{'='*80}")
            print(f"  SEASON {i}/{len(self.seasons)}: {season-1}-{season}")
            print(f"{'='*80}")
            
            game_logs = self.get_player_game_logs(season)
            if not game_logs.empty:
                game_logs['season_weight'] = self.weights.get(season, 0.25)
                data['game_logs'].append(game_logs)
            
            # Get standings
            standings = self.get_team_standings(season)
            if not standings.empty:
                data['standings'].append(standings)
            
            # Wait between seasons to be extra cautious
            if i < len(self.seasons):
                print(f"\n⏸  Waiting 60 seconds before next season...")
                time.sleep(60)
        
        # Combine all game logs
        if data['game_logs']:
            data['game_logs'] = pd.concat(data['game_logs'], ignore_index=True)
            print(f"\n✅ Total game logs collected: {len(data['game_logs'])}")
        else:
            data['game_logs'] = pd.DataFrame()
            print(f"\n⚠️  No game logs collected")
        
        # Combine standings
        if data['standings']:
            data['standings'] = pd.concat(data['standings'], ignore_index=True)
            print(f"✅ Total standings collected: {len(data['standings'])}")
        else:
            data['standings'] = pd.DataFrame()
            print(f"⚠️  No standings collected")
        
        # Get injury data (current season focus)
        data['injury_data'] = self.get_injury_data()
        
        print("\n" + "="*80)
        print("  DATA COLLECTION COMPLETE")
        print("="*80 + "\n")
        
        return data
    
    def save_data(self, data, output_dir='data'):
        """Save collected data to disk"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nSaving data to {output_dir}/...")
        
        if not data['game_logs'].empty:
            # Convert enum objects to strings for serialization
            game_logs_clean = data['game_logs'].copy()
            
            # Convert any enum columns to strings
            for col in game_logs_clean.columns:
                if game_logs_clean[col].dtype == 'object':
                    try:
                        game_logs_clean[col] = game_logs_clean[col].astype(str)
                    except:
                        pass
            
            # Try parquet first, fall back to CSV
            try:
                game_logs_clean.to_parquet(f'{output_dir}/game_logs.parquet', index=False)
                print(f"✅ Saved game logs (parquet): {len(game_logs_clean)} records")
            except Exception as e:
                print(f"⚠️  Parquet save failed ({e}), using CSV instead...")
                game_logs_clean.to_csv(f'{output_dir}/game_logs.csv', index=False)
                print(f"✅ Saved game logs (csv): {len(game_logs_clean)} records")
        
        if not data['standings'].empty:
            data['standings'].to_csv(f'{output_dir}/standings.csv', index=False)
            print(f"✅ Saved standings: {len(data['standings'])} records")
        
        if data['injury_data'] is not None and not data['injury_data'].empty:
            data['injury_data'].to_csv(f'{output_dir}/injury_data.csv', index=False)
            print(f"✅ Saved injury data: {len(data['injury_data'])} records")
        
        print(f"\n✅ All data saved to {output_dir}/")


if __name__ == "__main__":
    # Test the collector
    collector = NBADataCollector(seasons=[2024, 2025])
    data = collector.collect_all_data()
    collector.save_data(data)