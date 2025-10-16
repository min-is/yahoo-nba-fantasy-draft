# NBA Fantasy Basketball Draft Tool 🏀

Advanced machine learning-powered draft assistant for Yahoo Fantasy Basketball (2025-26 season)

## Overview

This tool provides data-driven player rankings optimized for **your specific league settings**, prioritizing:
- **Consistency** over volatility (predictable week-to-week performance)
- **Injury risk modeling** (games missed, playing time trends)
- **Age-adjusted projections** (accounting for prime years and decline)
- **Team context** (contenders vs tanking teams)

Built specifically for **Yahoo Fantasy Basketball** with custom scoring: PTS(1), REB(1.2), AST(1.5), STL(3), BLK(3), TO(-1)

---

## Features

### 🎯 Smart Rankings
- **XGBoost ML Model**: Projects fantasy points using 4 years of historical data
- **Optimized Moving Averages**: Automatically weights recent performance
- **Consistency Metrics**: Statistical reliability scores (coefficient of variation, IQR ratios)
- **Floor/Ceiling Analysis**: 10th and 90th percentile performance benchmarks

### 📊 Visual Analytics
- Game-by-game performance charts
- Statistical distribution plots
- Comparative metrics radar charts
- Detailed player profiles for top prospects

### 🔴 Real-Time Draft Tracker
- Interactive tool for live draft
- Snake draft logic (calculates when your next pick is)
- Filters out drafted players automatically
- Quick player search functionality

### 📈 Advanced Features
- **Injury Risk Scores**: Based on games missed, minutes volatility, and historical injuries
- **Age Adjustment Curves**: Peak performance at 25-29 years
- **VORP**: Value Over Replacement Player calculations
- **Team Context**: Playoff team vs tanking team identification

---

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Launch notebook
jupyter notebook NBA_Fantasy_Draft_Tool.ipynb
```

### First Run (20-30 min)
```python
# The notebook will automatically:
# 1. Scrape 4 seasons of NBA data (2022-2025)
# 2. Engineer 180+ advanced features
# 3. Train XGBoost prediction model
# 4. Generate player rankings
# 5. Export Excel draft guide
```

### During Your Draft
```python
# Update your draft position
your_pick_position = 6  # Your actual pick number

# Mark players as drafted
tracker.mark_player_drafted("Nikola Jokic", by_you=False)
tracker.display_status()  # Shows top available players
```

See **[QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md)** for detailed instructions.

---

## Output Files

| File | Description |
|------|-------------|
| `data/draft_rankings.csv` | Complete player rankings with all metrics |
| `NBA_Fantasy_Draft_Guide_2025.xlsx` | Multi-sheet Excel guide (Overall, Top 100, Most Consistent, etc.) |
| `data/player_features.csv` | Engineered features for all players |
| `data/game_logs.parquet` | Cached game-by-game data |

---

## Methodology

### Data Collection
- **Source**: Basketball-Reference.com (via `basketball-reference-web-scraper`)
- **Seasons**: 2021-22 through 2024-25
- **Weighting**: Recent seasons weighted more heavily (2025: 40%, 2024: 30%, 2023: 20%, 2022: 10%)
- **Supplemental**: RotoWire injury data, team standings

### Feature Engineering

**Player-Level Features:**
- Optimized weighted moving averages (15-30 game windows)
- Consistency scores (coefficient of variation, IQR ratios)
- Usage metrics (minutes, shot attempts, usage rate)
- Counting stats (points, rebounds, assists, stocks)

**Risk Factors:**
- Injury risk score (0-100 scale)
- Age adjustment multiplier
- Games played trends
- Minutes volatility

**Team Context:**
- Playoff probability
- Pace and efficiency
- Contender vs tanking classification

### Machine Learning Model

**Algorithm**: XGBoost Regressor
- Objective: Predict season-long fantasy points per game
- Training: Walk-forward cross-validation
- Features: 16 core metrics + engineered features
- Hyperparameters: Optimized via grid search

**Performance** (typical):
- MAE: ~6.5 fantasy points/game
- RMSE: ~8.5 fantasy points/game
- R²: ~0.85

---

## Customization

### Change Scoring System
Edit `data_collector.py`:
```python
self.yahoo_scoring = {
    'points_scored': 1.0,  # Modify these
    'rebounds': 1.2,
    'assists': 1.5,
    '