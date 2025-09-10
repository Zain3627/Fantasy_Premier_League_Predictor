# ⚽ Fantasy Premier League Predictor

A sophisticated machine learning-powered Fantasy Premier League (FPL) player performance predictor that helps you make informed decisions for your fantasy team. This tool uses advanced XGBoost models with hyperparameter optimization to predict player points across multiple gameweeks.

## 🌟 Features

### 🤖 **Advanced Machine Learning**
- **XGBoost Regression Models** with position-specific tuning

### 📊 **Comprehensive Data Analysis**
- **Real-time FPL API integration** for live player data
- **Historical performance analysis** with 3-year average calculations
- **Rolling averages** for recent form evaluation
- **Team strength analysis** including home/away performance
- **Fixture difficulty assessment**

### 🎯 **Position-Specific Predictions**
- **Goalkeepers**: Specialized models considering saves, clean sheets, goals conceded
- **Defenders**: Focus on defensive contributions, clean sheets, attacking returns
- **Midfielders**: Balanced approach considering goals, assists, creativity
- **Forwards**: Emphasis on goals, expected goals, attacking threat

### 🔧 **Advanced Feature Engineering**
- **Cross-team features**: Opponent attacking/defensive strength analysis
- **Strength differentials**: Team vs opponent comparisons
- **Home advantage factors**: Home/away performance adjustments
- **Recent form metrics**: 3-game rolling averages
- **Expected goals integration**: xG, xA, xGI considerations

### 🖥️ **Interactive Web Interface**
- **Streamlit web application** with clean, professional UI
- **Position-based result tabs** with sortable data tables
- **Top picks highlighting** for each position
- **Export capabilities** with CSV downloads

## 🚀 Quick Start

### Prerequisites
```bash
pip install streamlit pandas numpy scikit-learn xgboost requests
```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/fantasy-premier-league-predictor.git
cd fantasy-premier-league-predictor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

4. Or run via command line:
```bash
python main.py
```

## 📁 Project Structure

```
fantasy/
├── streamlit_app.py           # Web interface
├── main.py                    # Command line interface
├── FantasyPredicorPipeline.py # Main prediction pipeline
├── FantasyModel.py            # ML models with hyperparameter tuning
├── DataLoader.py              # FPL API data loading
├── DataPreprocessing.py       # Data cleaning and preprocessing
├── FeatureEngineering.py      # Advanced feature creation
├── predictions/               # Output CSV files
└── logs/                      # Training logs and debug files
```

## 🎮 How to Use

### Web Interface
1. **Launch**: Run `streamlit run streamlit_app.py`
2. **Select gameweeks**: Choose start and end gameweeks (e.g., 4-6)
3. **Generate predictions**: Click "Generate Predictions" button
4. **View results**: Browse through position tabs to see top players
5. **Download**: CSV files are automatically saved in `predictions/` folder

### Command Line
```python
from FantasyPredicorPipeline import FantasyPredicorPipeline
import DataLoader as dl
import DataPreprocessing as dp
# ... other imports

# Initialize pipeline
pipeline = FantasyPredicorPipeline(loader, preprocessor, models...)

# Generate predictions for gameweeks 4-6
results = pipeline.run(4, 6)
```

## 📈 Model Performance

### Model Architecture
- **Goalkeepers**: XGBoost with specialized defensive metrics
- **Defenders**: Focus on clean sheets and defensive contributions
- **Midfielders/Forwards**: Emphasis on attacking returns and creativity

### Hyperparameter Optimization
- **20 random combinations** tested per model
- **3-fold cross-validation** for robust evaluation
- **Position-specific parameter ranges**:
  - Learning rates: 0.005-0.2
  - Tree depths: 3-10
  - Estimators: 100-1000

### Feature Importance
- Historical performance (30%)
- Recent form (25%)
- Fixture difficulty (20%)
- Team strength (15%)
- Cross-team analysis (10%)

## 📊 Output Format

### CSV Files
Generated for each position with columns:
- `web_name`: Player name
- `name`: Team name
- `gw_X`: Individual gameweek predictions
- `total_points`: Sum across all gameweeks

### Web Interface
- **Interactive tables** with sortable columns
- **Top picks cards** showing best players per position
- **Formatted numbers** with 2 decimal places
- **Clean design** without index columns

## 🔧 Configuration

### Model Parameters
Adjust in `FantasyModel.py`:
```python
param_distributions = {
    'n_estimators': [100, 200, 500, 1000],
    'learning_rate': [0.01, 0.05, 0.1, 0.15],
    'max_depth': [4, 6, 8, 10],
    # ... more parameters
}
```

### Feature Engineering
Customize in `FeatureEngineering.py`:
- Add new cross-team features
- Modify rolling window sizes
- Adjust strength calculations

## 🛠️ Technical Details

### Data Sources
- **FPL Official API**: Real-time player and fixture data
- **Historical data**: 3+ years of player performance
- **Team statistics**: Strength ratings and form

### Performance Optimizations
- **Efficient API calls** with error handling
- **Vectorized operations** for large datasets
- **Memory optimization** with data type management
- **Progress tracking** for long-running operations

### Error Handling
- **API timeout management**
- **Missing data imputation**
- **Model validation checks**
- **Graceful failure recovery**

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=1.7.0
requests>=2.28.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fantasy Premier League** for providing the official API
- **XGBoost** team for the excellent ML framework
- **Streamlit** for the intuitive web framework
- **Fantasy football community** for inspiration and feedback

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Questions**: Discussion in GitHub Discussions
- **Features**: Submit feature requests with detailed descriptions

## 🔄 Recent Updates

- ✅ Added RandomizedSearchCV for hyperparameter optimization
- ✅ Implemented cross-team feature engineering
- ✅ Enhanced web interface with progress tracking
- ✅ Improved result formatting and display
- ✅ Added comprehensive error handling

---

**Made with ❤️ for the Fantasy Premier League community**

*Disclaimer: This tool is for educational and entertainment purposes. Past performance does not guarantee future results in Fantasy Premier League.*
