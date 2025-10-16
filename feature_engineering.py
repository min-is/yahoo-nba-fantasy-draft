"""
Feature Engineering for NBA Fantasy Predictions
Creates advanced features including consistency scores, injury risk, and optimized moving averages
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class FantasyFeatureEngineer:
    """Creates advanced features for fantasy basketball prediction"""
    
    def __init__(self, game_logs_df, injury_df=None, standings_df=None):
        """
        Args:
            game_logs_df: DataFrame with player game logs
            injury_df: DataFrame with injury history
            standings_df: DataFrame with team standings
        """
        self.game_logs = game_logs_df.copy()
        self.injury_data = injury_df
        self.standings = standings_df
        
    def calculate_consistency_metrics(self, player_games, min_games=10):
        """
        Calculate statistical consistency metrics for a player
        Uses coefficient of variation and percentile-based measures
        
        Returns dict of consistency metrics
        """
        if len(player_games) < min_games:
            return {
                'consistency_score': 0,
                'floor': 0,
                'ceiling': 0,
                'avg_fp': 0,
                'std_fp': 0,
                'coef_variation': 0,
                'iqr_ratio': 0
            }
        
        fp = player_games['fantasy_points'].values
        
        # Basic stats
        avg_fp = np.mean(fp)
        std_fp = np.std(fp)
        
        # Coefficient of Variation (lower is more consistent)
        coef_var = std_fp / avg_fp if avg_fp > 0 else 0
        
        # Percentile-based metrics
        floor = np.percentile(fp, 10)  # 10th percentile (bad games)
        ceiling = np.percentile(fp, 90)  # 90th percentile (great games)
        median = np.median(fp)
        
        # IQR ratio (measures spread relative to median)
        q75, q25 = np.percentile(fp, [75, 25])
        iqr = q75 - q25
        iqr_ratio = iqr / median if median > 0 else 0
        
        # Consistency Score: Higher is better
        # Combines low coefficient of variation with high floor
        # Penalizes high variance relative to mean
        consistency_score = (avg_fp * 0.5) + (floor * 0.3) - (coef_var * avg_fp * 0.2)
        
        return {
            'consistency_score': consistency_score,
            'floor': floor,  # 10th percentile
            'ceiling': ceiling,  # 90th percentile
            'avg_fp': avg_fp,
            'median_fp': median,
            'std_fp': std_fp,
            'coef_variation': coef_var,  # Lower is more consistent
            'iqr_ratio': iqr_ratio,  # Lower is more consistent
            'games_played': len(player_games)
        }
    
    def create_optimized_moving_averages(self, player_games, feature_col='fantasy_points', 
                                        look_back=20, train_cutoff_date='2024-01-01'):
        """
        Create optimized weighted moving averages using linear regression
        Adapts the method from the reference project
        
        Args:
            player_games: DataFrame of games for a single player
            feature_col: Column to create moving average for
            look_back: Number of games to look back
            train_cutoff_date: Don't use games after this date for optimization
        
        Returns optimized moving average values
        """
        if len(player_games) < look_back:
            return np.zeros(len(player_games))
        
        player_games = player_games.sort_values('date').reset_index(drop=True)
        
        # Create lag features
        lag_features = pd.DataFrame()
        for lag in range(1, look_back + 1):
            lag_features[f'lag_{lag}'] = player_games[feature_col].shift(lag)
        
        # Fill NaN with 0
        lag_features = lag_features.fillna(0)
        
        # Split training data (use historical data to optimize weights)
        if 'date' in player_games.columns:
            train_mask = pd.to_datetime(player_games['date']) < pd.to_datetime(train_cutoff_date)
            if train_mask.sum() > look_back:
                X_train = lag_features[train_mask]
                y_train = player_games.loc[train_mask, feature_col]
                
                # Fit linear regression to find optimal weights
                lr = LinearRegression(fit_intercept=True)
                lr.fit(X_train, y_train)
                
                # Apply optimized weights to all data
                optimized_ma = lr.predict(lag_features)
                return optimized_ma
        
        # Fallback to simple exponential moving average if optimization fails
        ema = player_games[feature_col].ewm(span=look_back, adjust=False).mean().values
        return ema
    
    def calculate_injury_risk_score(self, player_name, recent_games):
        """
        Calculate injury risk based on:
        1. Games missed in recent season
        2. Historical injury data
        3. Minutes played trends
        
        Returns risk score (0-100, higher = more risk)
        """
        risk_score = 0
        
        # Factor 1: Games missed (assuming 82 game season)
        games_played = len(recent_games)
        expected_games = 82  # Can adjust based on actual season progress
        
        if games_played < expected_games * 0.7:  # Missed 30%+ of games
            risk_score += 30
        elif games_played < expected_games * 0.85:  # Missed 15%+ of games
            risk_score += 15
        
        # Factor 2: Minutes played volatility
        if 'seconds_played' in recent_games.columns:
            minutes = recent_games['seconds_played'] / 60
            if len(minutes) > 5:
                minutes_std = minutes.std()
                minutes_mean = minutes.mean()
                if minutes_mean > 0:
                    minutes_cv = minutes_std / minutes_mean
                    risk_score += min(20, minutes_cv * 50)  # Cap at 20 points
        
        # Factor 3: Recent injury history from injury_data
        if self.injury_data is not None and not self.injury_data.empty:
            player_injuries = self.injury_data[
                self.injury_data['player_name'] == player_name
            ]
            if len(player_injuries) > 0:
                risk_score += min(30, len(player_injuries) * 10)
        
        # Factor 4: Trend in games played (getting worse?)
        if games_played < 60:
            risk_score += 20
        
        return min(100, risk_score)  # Cap at 100
    
    def calculate_age_adjustment(self, age):
        """
        Calculate age-based performance multiplier
        Peak years: 25-29 (multiplier = 1.0)
        Younger: slight penalty for inexperience
        Older: decline curve
        """
        if pd.isna(age):
            return 1.0
        
        if age < 23:
            # Young players - slight upside potential
            return 0.95 + (age - 20) * 0.025
        elif 23 <= age <= 29:
            # Prime years
            return 1.0
        elif 30 <= age <= 33:
            # Early decline
            return 1.0 - (age - 29) * 0.03
        else:
            # Steeper decline after 33
            return 0.88 - (age - 33) * 0.05
    
    def add_team_context(self):
        """
        Add team-level features:
        - Contender vs tanking team
        - Team pace/efficiency
        - Playoff probability
        """
        if self.standings is None or self.standings.empty:
            self.game_logs['is_contender'] = True  # Default assumption
            return
        
        # Merge team standings info
        team_mapping = self.standings.set_index(['Team', 'season_end_year'])['is_contender'].to_dict()
        
        self.game_logs['is_contender'] = self.game_logs.apply(
            lambda row: team_mapping.get((row.get('team', ''), row.get('season_end_year', 2025)), True),
            axis=1
        )
    
    def create_all_features(self):
        """
        Main method to create all features
        Returns enhanced DataFrame
        """
        print("\nCreating advanced features...")
        
        # Ensure data is sorted
        self.game_logs = self.game_logs.sort_values(['player_name', 'date']).reset_index(drop=True)
        
        # Initialize feature columns
        feature_cols = [
            'consistency_score', 'floor', 'ceiling', 'avg_fp', 'median_fp',
            'std_fp', 'coef_variation', 'iqr_ratio', 'optimized_ma_fp',
            'optimized_ma_points', 'optimized_ma_rebounds', 'optimized_ma_assists',
            'injury_risk_score', 'age_adjustment', 'games_played_count'
        ]
        
        for col in feature_cols:
            self.game_logs[col] = 0.0
        
        # Group by player and calculate features
        player_features = []
        
        for player_name, player_games in self.game_logs.groupby('player_name'):
            player_games = player_games.sort_values('date').reset_index(drop=True)
            
            # 1. Consistency metrics (use last season's data)
            recent_season = player_games[
                player_games['season_end_year'] == player_games['season_end_year'].max()
            ]
            consistency = self.calculate_consistency_metrics(recent_season)
            
            # 2. Optimized moving averages
            opt_ma_fp = self.create_optimized_moving_averages(
                player_games, 'fantasy_points', look_back=20
            )
            
            # Also create for individual stats
            opt_ma_pts = self.create_optimized_moving_averages(
                player_games, 'points_scored', look_back=15
            ) if 'points_scored' in player_games.columns else np.zeros(len(player_games))
            
            opt_ma_reb = self.create_optimized_moving_averages(
                player_games, 'offensive_rebounds', look_back=15
            ) if 'offensive_rebounds' in player_games.columns else np.zeros(len(player_games))
            
            opt_ma_ast = self.create_optimized_moving_averages(
                player_games, 'assists', look_back=15
            ) if 'assists' in player_games.columns else np.zeros(len(player_games))
            
            # 3. Injury risk
            injury_risk = self.calculate_injury_risk_score(player_name, recent_season)
            
            # 4. Age adjustment
            age = player_games['age'].iloc[-1] if 'age' in player_games.columns else 27
            age_adj = self.calculate_age_adjustment(age)
            
            # Create feature row for this player (using most recent values)
            player_feature = {
                'player_name': player_name,
                'player_slug': player_games['player_slug'].iloc[-1] if 'player_slug' in player_games.columns else '',
                **consistency,
                'optimized_ma_fp': opt_ma_fp[-1] if len(opt_ma_fp) > 0 else 0,
                'optimized_ma_points': opt_ma_pts[-1] if len(opt_ma_pts) > 0 else 0,
                'optimized_ma_rebounds': opt_ma_reb[-1] if len(opt_ma_reb) > 0 else 0,
                'optimized_ma_assists': opt_ma_ast[-1] if len(opt_ma_ast) > 0 else 0,
                'injury_risk_score': injury_risk,
                'age_adjustment': age_adj,
                'age': age
            }
            
            player_features.append(player_feature)
        
        # Combine into DataFrame
        features_df = pd.DataFrame(player_features)
        
        # Add team context
        self.add_team_context()
        
        # Merge team info into features
        team_info = self.game_logs.groupby('player_name').agg({
            'is_contender': 'last',
            'team': 'last',
            'season_end_year': 'max'
        }).reset_index()
        
        features_df = features_df.merge(team_info, on='player_name', how='left')
        
        print(f"Created features for {len(features_df)} players")
        
        return features_df


if __name__ == "__main__":
    # Test feature engineering
    print("Feature engineering module loaded successfully")