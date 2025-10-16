# NBA Fantasy Draft Tool - Quick Start Guide

## 🚀 Setup (15 minutes)

### 1. Install Requirements
```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. First Run - Data Collection
```bash
# Launch Jupyter Notebook
jupyter notebook NBA_Fantasy_Draft_Tool.ipynb
```

**Important:** The first run will take 20-30 minutes to scrape historical data from Basketball-Reference. This data will be cached for future use.

### 3. Run All Cells
- Click "Cell" → "Run All" in Jupyter
- Wait for data collection and model training to complete
- Review the generated rankings

---

## 📊 What You'll Get

### 1. **Player Rankings** (`data/draft_rankings.csv`)
- Projected fantasy points per game (Yahoo scoring)
- Consistency scores (lower variance = better)
- Floor (10th percentile) and Ceiling (90th percentile)
- Injury risk scores
- Age-adjusted projections

### 2. **Excel Draft Guide** (`NBA_Fantasy_Draft_Guide_2025.xlsx`)
Multiple sheets:
- Overall Rankings (all players)
- Top 100 
- Most Consistent (reliable performers)
- Healthy Players (low injury risk)
- High Ceiling (boom/bust candidates)

### 3. **Player Visualizations**
Comprehensive charts for top players showing:
- Game-by-game fantasy point trends
- Statistical distributions
- Key metric comparisons
- Detailed summaries

### 4. **Interactive Draft Tracker**
Real-time tool for your live draft

---

## 🎯 Using During Your Draft (Monday Oct 20)

### Pre-Draft (30 min before)
1. **Update your draft position:**
   ```python
   # In the notebook, find this cell and update:
   your_pick_position = 6  # CHANGE THIS to your actual pick
   ```

2. **Print or open the Excel file** for quick reference

3. **Review top 20 players** and memorize your targets

### During Draft

**Option A: Use the Interactive Tracker**
```python
# Mark each pick as it happens
player_name = "Nikola Jokic"  # Change this
by_you = False  # Set True if you picked them

tracker.mark_player_drafted(player_name, by_you=by_you)
tracker.display_status()
```

**Option B: Use Excel Guide**
- Keep the file open and cross off players as they're drafted
- Focus on "Most Consistent" tab for safe picks
- Check "High Ceiling" tab for upside plays

### Quick Player Lookup
```python
# Search for any player
search_player("Curry")  # Returns all Currys with their rankings
```

---

## 🔑 Key Metrics Explained

### Adjusted Projection
Your expected fantasy points per game. Accounts for:
- Historical performance (weighted toward recent seasons)
- Age (peak = 25-29 years)
- Injury risk
- Team situation (contender vs tanking)

### Consistency Score
Higher = more predictable. Combines:
- Low coefficient of variation (consistent game-to-game)
- High floor (reliable minimum output)
- Penalizes high variance players

**Best for:** Risk-averse drafters who want reliable weekly scores

### Floor vs Ceiling
- **Floor**: 10th percentile game (bad night)
- **Ceiling**: 90th percentile game (great night)
- **High floor players** → Consistent (SGA, Jokic)
- **High ceiling players** → Boom/bust (young players, injury-prone stars)

### Injury Risk Score
0-100 scale (lower is better):
- **0-25**: Very healthy (played 70+ games, stable minutes)
- **26-50**: Some concern (missed 10-20 games)
- **51-75**: Significant risk (missed 20+ games)
- **76-100**: High risk (major injury history)

### VORP (Value Over Replacement Player)
Points above a "replacement level" player (bottom 40th percentile).
- Helps identify true difference-makers vs. streamer-level players

---

## 📋 Draft Strategy Tips

### Round 1-3: Elite Tier
- Prioritize **consistency + projection**
- Avoid injury risks in early rounds
- Target players on contending teams
- SGA, Jokic, Giannis types

### Round 4-7: Solid Contributors
- Look for **high floor** players
- Balance positions (don't draft 3 centers)
- Consider age (avoid 33+ unless elite)

### Round 8-10: Value Hunting
- Target **underrated consistent** players
- Check "Most Consistent" sheet
- Young players with rising usage

### Round 11-13: Upside Swings
- Draft high ceiling players
- Injury-prone stars (if healthy = league winner)
- Young players with opportunity

---

## 🛠️ Troubleshooting

### Data Collection Fails
**Problem:** `basketball_reference_web_scraper` throws errors

**Solution:** The scraper package can be flaky. If it fails:
1. Try running the cell again (Basketball-Reference may have rate limited you)
2. Wait 5 minutes and retry
3. If persistent, you may need to use alternative data sources or cached data

### Missing Player Data
**Problem:** A specific player isn't in the rankings

**Reasons:**
- Played fewer than 30 games last season (minimum threshold)
- Rookie (no historical data)
- International player not in NBA yet

**Solution:** Manually research the player on Basketball-Reference

### Jupyter Kernel Crashes
**Problem:** Notebook freezes during data collection

**Solution:**
- Reduce number of seasons: `seasons=[2024, 2025]` (just 2 years)
- Close other programs to free RAM
- Run in smaller batches

---

## 📁 File Structure

```
project/
├── requirements.txt                    # Python dependencies
├── QUICKSTART_GUIDE.md                # This file
├── NBA_Fantasy_Draft_Tool.ipynb       # Main notebook
├── data_collector.py                  # Scrapes NBA data
├── feature_engineering.py             # Creates advanced features
├── data/                              # Generated data (cached)
│   ├── game_logs.parquet             # Raw game data
│   ├── player_features.csv           # Engineered features
│   └── draft_rankings.csv            # Final rankings
└── NBA_Fantasy_Draft_Guide_2025.xlsx  # Excel export
```

---

## 💡 Advanced Usage

### Customize Scoring System
If your league uses different points, edit in `data_collector.py`:
```python
self.yahoo_scoring = {
    'points_scored': 1.0,    # Change these
    'rebounds': 1.2,
    'assists': 1.5,
    'steals': 3.0,
    'blocks': 3.0,
    'turnovers': -1.0
}
```

### Adjust Weights
Prefer more recent seasons? Edit in `data_collector.py`:
```python
weights={2025: 0.50, 2024: 0.30, 2023: 0.15, 2022: 0.05}
```

### Add Custom Features
Edit `feature_engineering.py` to add your own metrics

---

## ⚠️ Important Notes

1. **Data Currency**: Data is current as of when you run the scraper. For draft on Oct 20, run the notebook on Oct 19 to get most recent data.

2. **Preseason Games**: The model does NOT include 2024-25 regular season games (since season hasn't started). Projections based on 2024 and prior seasons.

3. **Rookie Players**: Will not appear in rankings (no historical data). Research separately.

4. **Position Eligibility**: You may need to manually verify positions on Yahoo's site, as this can change year-to-year.

5. **Updates**: Rerun the entire notebook to refresh with new data.

---

## 🎉 You're Ready!

Before your draft:
- ✅ Run notebook to generate rankings
- ✅ Export to Excel  
- ✅ Review top 30 players
- ✅ Set your draft position
- ✅ Print cheat sheet or keep Excel open

**Good luck with your draft!** 🏀