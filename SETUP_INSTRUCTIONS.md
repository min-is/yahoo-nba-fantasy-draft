# Complete Setup Instructions

## 📁 Project Structure

Create a new directory for your project and organize files like this:

```
NBA_Fantasy_Draft_Tool/
│
├── requirements.txt                    # Python dependencies
├── README.md                          # Full documentation
├── QUICKSTART_GUIDE.md                # Quick start instructions
├── SETUP_INSTRUCTIONS.md              # This file
│
├── data_collector.py                  # Data scraping module
├── feature_engineering.py             # Feature creation module
├── run_analysis.py                    # Command-line tool
├── NBA_Fantasy_Draft_Tool.ipynb       # Interactive notebook
│
└── data/                              # Generated data folder (auto-created)
    ├── game_logs.parquet              # Cached game data
    ├── standings.csv                  # Team standings
    ├── injury_data.csv                # Injury information
    ├── player_features.csv            # Engineered features
    └── draft_rankings.csv             # Final rankings
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create Project Directory

```bash
# Create main project folder
mkdir NBA_Fantasy_Draft_Tool
cd NBA_Fantasy_Draft_Tool

# Create data directory
mkdir data
```

### Step 2: Download/Create All Files

Save each of the following files I've provided into your project directory:

1. **requirements.txt** - Dependencies list
2. **README.md** - Full documentation
3. **QUICKSTART_GUIDE.md** - Quick start guide
4. **data_collector.py** - Data collection script
5. **feature_engineering.py** - Feature engineering script
6. **run_analysis.py** - Command-line runner
7. **NBA_Fantasy_Draft_Tool.ipynb** - Jupyter notebook

### Step 3: Set Up Python Environment

**Option A: Using venv (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using conda**
```bash
# Create conda environment
conda create -n nba_fantasy python=3.9

# Activate it
conda activate nba_fantasy

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Test imports
python -c "import pandas, numpy, xgboost, sklearn; print('✓ All packages installed!')"
```

---

## ▶️ Running the Tool

### Method 1: Command Line (Fastest)

```bash
# Generate all rankings and Excel guide
python run_analysis.py
```

**What happens:**
- Scrapes 4 seasons of NBA data (~20 minutes first time)
- Engineers 180+ features
- Trains XGBoost model
- Generates rankings
- Exports Excel guide

**Output files:**
- `data/draft_rankings.csv`
- `data/player_features.csv`
- `NBA_Fantasy_Draft_Guide_2025.xlsx`

### Method 2: Jupyter Notebook (Interactive)

```bash
# Start Jupyter
jupyter notebook

# Open: NBA_Fantasy_Draft_Tool.ipynb
# Click: Cell → Run All
```

**What you get:**
- All the command-line outputs PLUS:
- Interactive visualizations
- Player profile charts
- Real-time draft tracker
- Search functionality

---

## 🔧 Troubleshooting Setup

### Issue: "pip: command not found"

**Solution:**
```bash
# Try python3 and pip3
python3 -m pip install -r requirements.txt
```

### Issue: "No module named 'basketball_reference_web_scraper'"

**Solution:**
```bash
# Install it directly
pip install basketball-reference-web-scraper

# If that fails, try:
pip install basketball-reference-web-scraper --upgrade
```

### Issue: "Permission denied"

**Solution:**
```bash
# Use --user flag
pip install -r requirements.txt --user
```

### Issue: Jupyter won't start

**Solution:**
```bash
# Reinstall jupyter
pip uninstall jupyter
pip install jupyter

# Or try notebook directly
pip install notebook
jupyter notebook
```

### Issue: Data collection fails

**Symptoms:** 
```
Error: Connection timeout
Error: 403 Forbidden
```

**Solution:**
```bash
# Basketball-Reference may be rate limiting you
# Wait 5 minutes, then try again

# Or reduce data scope in data_collector.py:
# Change: seasons=[2022, 2023, 2024, 2025]
# To: seasons=[2024, 2025]  # Just 2 seasons
```

### Issue: Out of memory error

**Solution:**
```python
# In data_collector.py, reduce batch size:
# Change the loop to process fewer players at once

# Or reduce seasons to just [2024, 2025]
```

---

## ✅ Verification Checklist

Before running your first analysis, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] All 7 files in project directory
- [ ] Virtual environment activated
- [ ] All packages installed (`pip list | grep xgboost`)
- [ ] Data directory created
- [ ] Internet connection active (for scraping)

---

## 🎯 First Run Timeline

**Expected duration for first complete run:**

| Step | Time | What's Happening |
|------|------|------------------|
| Install packages | 2-5 min | Downloading dependencies |
| Data collection | 20-30 min | Scraping Basketball-Reference |
| Feature engineering | 2-3 min | Creating advanced metrics |
| Model training | 1-2 min | Training XGBoost |
| Visualization | 1-2 min | Generating charts |
| **Total** | **25-40 min** | **First run only** |

**Subsequent runs:** 3-5 minutes (data is cached!)

---

## 📊 What To Do After Setup

### Immediate Actions:

1. **Run the analysis**
   ```bash
   python run_analysis.py
   ```

2. **Review the output**
   - Open `NBA_Fantasy_Draft_Guide_2025.xlsx`
   - Check top 20 players
   - Review consistency scores

3. **Test the notebook**
   ```bash
   jupyter notebook NBA_Fantasy_Draft_Tool.ipynb
   ```

4. **Familiarize yourself with the tracker**
   - Practice marking players as drafted
   - Test the search function
   - Understand the display

### Before Draft Day:

1. **Rerun for fresh data** (Oct 19)
   ```bash
   python run_analysis.py
   ```

2. **Update your draft position**
   - Edit notebook Step 6
   - Change `your_pick_position = X`

3. **Review your targets**
   - Memorize top 30 players
   - Note high-consistency players
   - Identify value picks in rounds 7-10

4. **Print/prepare references**
   - Print top 100 from Excel
   - Have Excel file open
   - Bookmark player search cell

---

## 🆘 Getting Help

### Check These First:

1. **README.md** - Full documentation
2. **QUICKSTART_GUIDE.md** - Step-by-step instructions
3. **Code comments** - Each file has detailed comments

### Common Questions:

**Q: How do I update my league scoring?**
A: Edit `data_collector.py`, line ~20, modify the `yahoo_scoring` dictionary

**Q: Can I use this for ESPN/Sleeper?**
A: Yes, just update the scoring system in `data_collector.py`

**Q: How do I add rookies?**
A: Rookies won't appear (no historical data). Research them separately and add manually.

**Q: What if a player got traded?**
A: The model uses most recent team data. Manually consider new role/opportunity.

**Q: Can I run this on Windows/Mac/Linux?**
A: Yes, all platforms supported. Python is cross-platform.

---

## 🔄 Updating the Tool

### Refresh Data Before Draft:

```bash
# Delete cached data
rm -rf data/*.parquet data/*.csv

# Rerun analysis
python run_analysis.py

# This fetches fresh data
```

### Modify for Your League:

1. **Change scoring weights**
   - Edit `data_collector.py`
   - Modify `yahoo_scoring` dictionary

2. **Adjust draft score formula**
   - Edit notebook Step 4
   - Change projection/consistency/floor weights

3. **Add custom features**
   - Edit `feature_engineering.py`
   - Add new calculations in `create_all_features()`

---

## 📝 Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run analysis
python run_analysis.py

# Start notebook
jupyter notebook

# Update dependencies
pip install -r requirements.txt --upgrade

# Check versions
pip list | grep -E "pandas|xgboost|scikit"

# Deactivate environment
deactivate
```

---

## 🎉 You're Ready!

Once you've completed these steps, you should have:

✅ Complete working environment
✅ All dependencies installed  
✅ Project files organized
✅ Data collection tested
✅ Rankings generated
✅ Excel guide exported
✅ Notebook functional

**Next:** Review your rankings and prepare for draft day!

---

## 💡 Pro Tips

1. **Cache is your friend**: First run takes 30 min, subsequent runs take 3 min
2. **Test before draft day**: Run through the entire process at least once
3. **Have backup**: Print Excel guide in case computer issues during draft
4. **Trust the model**: It's more objective than gut feel, especially for consistency
5. **But override when needed**: Breaking news > historical data

**Good luck with your draft! 🏀🏆**