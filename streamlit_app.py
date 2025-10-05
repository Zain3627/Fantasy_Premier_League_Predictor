import streamlit as st
import DataLoader as dl
import DataPreprocessing as dp
import FantasyPredicorPipeline as fpp
import FantasyModel as fm
import FeatureEngineering as fe
import pandas as pd
import time
import os
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Fantasy Premier League Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_predictions_data():
    base_path = os.path.join(os.path.dirname(__file__), "predictions")
    with st.spinner("📊 Loading cached stats data..."):
        try:
            positions = ['goalkeepers','defenders', 'midfielders', 'forwards']
        # Dictionary to store the final dataframes
            position_dictionary = {}
            
            for position_name in positions:
                csv_file_path = os.path.join(base_path, f"{position_name}.csv")
                final_df = pd.read_csv(csv_file_path)
                position_dictionary[position_name] = final_df
            return position_dictionary
                
        except Exception as e:
            st.error(f"❌ Error loading predictions data try again later")
            return {}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_stats(name):
    base_path = os.path.join(os.path.dirname(__file__), "stats")
    with st.spinner("📊 Loading cached stats data..."):
        try:
            csv_file_path = os.path.join(base_path, f"{name}.csv")
            final_df = pd.read_csv(csv_file_path)
            return final_df

        except Exception as e:
            st.error(f"❌ Error loading predictions data try again later")
            return pd.DataFrame()

def create_dream_team(position_dictionary, finished_gw):
    """Create dream team based on predicted points for the next gameweek."""
    try:
        next_gw_col = f"gw_{finished_gw + 1}"
        
        # Check if we have prediction data
        all_positions_available = all(pos in position_dictionary for pos in ['goalkeepers', 'defenders', 'midfielders', 'forwards'])
        
        if not all_positions_available:
            return None
            
        # Combine all position data with position labels
        dream_team_data = []
        
        # Add goalkeepers (need 2)
        if 'goalkeepers' in position_dictionary and not position_dictionary['goalkeepers'].empty:
            gk_df = position_dictionary['goalkeepers'].copy()
            gk_df['position'] = 'Goalkeeper'
            dream_team_data.append(gk_df)
        
        # Add defenders (need 5)
        if 'defenders' in position_dictionary and not position_dictionary['defenders'].empty:
            def_df = position_dictionary['defenders'].copy()
            def_df['position'] = 'Defender'
            dream_team_data.append(def_df)
        
        # Add midfielders (need 5)
        if 'midfielders' in position_dictionary and not position_dictionary['midfielders'].empty:
            mid_df = position_dictionary['midfielders'].copy()
            mid_df['position'] = 'Midfielder'
            dream_team_data.append(mid_df)
        
        # Add forwards (need 3)
        if 'forwards' in position_dictionary and not position_dictionary['forwards'].empty:
            fwd_df = position_dictionary['forwards'].copy()
            fwd_df['position'] = 'Forward'
            dream_team_data.append(fwd_df)
        
        if not dream_team_data:
            return None
            
        # Combine all data
        all_players = pd.concat(dream_team_data, ignore_index=True)
        
        # Check if we have points column for the next gameweek
        if next_gw_col not in all_players.columns:
            st.error(f"Predictions for Gameweek {finished_gw + 1} (column '{next_gw_col}') not found.")
            return None
            
        # Sort by next gameweek points
        all_players = all_players.sort_values(next_gw_col, ascending=False)
        
        # Select dream team players
        dream_team = {
            'goalkeepers': [],
            'defenders': [],
            'midfielders': [],
            'forwards': []
        }
        
        # Select top players by position
        gk_players = all_players[all_players['position'] == 'Goalkeeper'].head(2)
        def_players = all_players[all_players['position'] == 'Defender'].head(5)
        mid_players = all_players[all_players['position'] == 'Midfielder'].head(5)
        fwd_players = all_players[all_players['position'] == 'Forward'].head(3)
        
        # Store in dream team dict
        for _, player in gk_players.iterrows():
            dream_team['goalkeepers'].append(player)
        for _, player in def_players.iterrows():
            dream_team['defenders'].append(player)
        for _, player in mid_players.iterrows():
            dream_team['midfielders'].append(player)
        for _, player in fwd_players.iterrows():
            dream_team['forwards'].append(player)
        
        # Create starting XI based on rules
        starting_xi = []
        substitutes = []
        
        # Add 1 goalkeeper (best one)
        if dream_team['goalkeepers']:
            starting_xi.append(dream_team['goalkeepers'][0])
            if len(dream_team['goalkeepers']) > 1:
                substitutes.append(dream_team['goalkeepers'][1])
        
        # Add 3 best defenders
        for i, defender in enumerate(dream_team['defenders'][:3]):
            starting_xi.append(defender)
        # Remaining defenders go to substitutes
        for defender in dream_team['defenders'][3:]:
            substitutes.append(defender)
        
        # Add 2 best midfielders
        for i, midfielder in enumerate(dream_team['midfielders'][:2]):
            starting_xi.append(midfielder)
        # Remaining midfielders go to substitutes
        for midfielder in dream_team['midfielders'][2:]:
            substitutes.append(midfielder)
        
        # Add 1 best forward
        if dream_team['forwards']:
            starting_xi.append(dream_team['forwards'][0])
            # Remaining forwards go to substitutes
            for forward in dream_team['forwards'][1:]:
                substitutes.append(forward)
        
        # Add more players to starting XI (up to 11) based on highest points
        remaining_players = []
        for defender in dream_team['defenders'][3:]:
            remaining_players.append(defender)
        for midfielder in dream_team['midfielders'][2:]:
            remaining_players.append(midfielder)
        for forward in dream_team['forwards'][1:]:
            remaining_players.append(forward)
        
        # Sort remaining players by points and add to starting XI
        remaining_players = sorted(remaining_players, key=lambda x: x[next_gw_col], reverse=True)
        
        while len(starting_xi) < 11 and remaining_players:
            player = remaining_players.pop(0)
            starting_xi.append(player)
            # Remove from substitutes if already there
            substitutes = [sub for sub in substitutes if not (hasattr(sub, 'name') and hasattr(player, 'name') and sub.name == player.name)]
        
        # Add remaining players to substitutes (up to 4)
        for player in remaining_players[:4-len(substitutes)]:
            if len(substitutes) < 4:
                substitutes.append(player)
        
        # Sort starting XI by points to determine captain and vice-captain
        starting_xi = sorted(starting_xi, key=lambda x: x[next_gw_col], reverse=True)
        
        return {
            'starting_xi': starting_xi,
            'substitutes': substitutes,
            'dream_team': dream_team,
            'points_col': next_gw_col
        }
        
    except Exception as e:
        st.error(f"Error creating dream team: {str(e)}")
        return None

# Initialize session state for active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "🎯 Predictions"

# Load all data only once and cache it
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if not st.session_state.data_loaded:
    with st.spinner("🔄 Loading all data..."):
        st.session_state.position_dictionary = load_predictions_data()
        st.session_state.teams_stats_for = load_stats("teams_for")
        st.session_state.teams_stats_against = load_stats("teams_against")
        st.session_state.goalkeepers_stats = load_stats("goalkeepers")
        st.session_state.defenders_stats = load_stats("defenders")
        st.session_state.passing_stats = load_stats('passing')
        st.session_state.shooting_stats = load_stats('shooting')
        st.session_state.data_loaded = True

# Use cached data from session state
position_dictionary = st.session_state.position_dictionary
teams_stats_for = st.session_state.teams_stats_for
teams_stats_against = st.session_state.teams_stats_against
goalkeepers_stats = st.session_state.goalkeepers_stats
defenders_stats = st.session_state.defenders_stats
passing_stats = st.session_state.passing_stats
shooting_stats = st.session_state.shooting_stats

# Custom CSS for green theme
st.markdown("""
<style>
    .main {
        background-color: #f0f8f0;
    }
    .stButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #218838;
    }
    .stNumberInput > div > div > input {
        border: 2px solid #28a745;
        border-radius: 5px;
    }
    .title {
        color: #155724;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .subtitle {
        color: #155724;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .prediction-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .stats-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_initialized' not in st.session_state:
    st.session_state.pipeline_initialized = False
    st.session_state.pipeline = None

# Title and header
st.markdown('<h1 class="title">⚽ Fantasy Premier League Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Predict player performance and analyze comprehensive statistics using advanced machine learning</p>', unsafe_allow_html=True)

# Main navigation with session state to remember active tab
tab_names = ["🎯 Predictions", "🏟️ Team Statistics", "👤 Player Statistics", "⭐ Dream Team"]

# Create tabs but track the active one
main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs(tab_names)

# Sidebar for information
with st.sidebar:
    st.markdown("### 📊 About")
    st.info("""
    This tool uses machine learning to predict Fantasy Premier League player performance based on:
    - Historical player data
    - Team statistics
    - Fixture difficulty
    - Recent form
    """)
    
    st.markdown("### 🎯 How to use")
    st.markdown("""
    1. Navigate through the tabs to explore different sections
    2. Use the Predictions tab to generate player predictions
    3. Explore Team Statistics for team performance insights
    4. Check Player Statistics for detailed player analysis
    5. View Dream Team for optimal squad selection
    """)
    
    # Current gameweek info
    try:
        loader = dl.DataLoader()
        deadlines = loader.load_data_api('https://fantasy.premierleague.com/api/bootstrap-static/','events')
        finished_gw = dp.DataPreprocessing().get_current_gw(deadlines) - 1
        st.markdown(f"### 📅 Current Status")
        st.success(f"Latest GW data update: **{7}**")
    except:
        finished_gw = 10
        st.warning("Could not fetch current gameweek")

# TAB 1: PREDICTIONS
with main_tab1:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔢 Select Gameweeks")
        
        # Input fields
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            start_gw = st.number_input(
                "Start Gameweek",
                min_value=finished_gw+1,
                max_value=min(finished_gw+5,38),
                value=finished_gw+1,
                help="Enter the starting gameweek number (1-38)"
            )
        
        with col_input2:
            end_gw = st.number_input(
                "End Gameweek", 
                min_value=finished_gw+1,
                max_value=min(finished_gw+5,38),
                value=finished_gw+3,
                help="Enter the ending gameweek number (1-38)"
            )
        
        # Validation
        if start_gw > end_gw:
            st.error("⚠️ Start gameweek must be less than or equal to end gameweek!")
        
        st.markdown("---")
        
        # Prediction button
        if st.button("🚀 Generate Predictions", use_container_width=True):
            if start_gw <= end_gw:
                with st.spinner('🔄 Initializing prediction pipeline...'):
                    if not st.session_state.pipeline_initialized:
                        try:
                            st.session_state.pipeline_initialized = True
                            st.success("✅ Pipeline initialized successfully!")
                        except Exception as e:
                            st.error(f"❌ Error initializing pipeline: {str(e)}")
                            st.stop()
                
                # Run predictions
                with st.spinner(f'🎯 Generating predictions for gameweeks {start_gw} to {end_gw}...'):
                    try:
                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        for i in range(100):
                            progress_bar.progress(i + 1)
                            if i < 20:
                                status_text.text('Loading player data...')
                            elif i < 40:
                                status_text.text('Processing team statistics...')
                            elif i < 60:
                                status_text.text('Training models...')
                            elif i < 80:
                                status_text.text('Generating predictions...')
                            else:
                                status_text.text('Finalizing results...')
                            time.sleep(0.02)
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Success message
                        st.success(f"🎉 Predictions generated successfully for gameweeks {start_gw} to {end_gw}!")
                        
                        # Display prediction results
                        st.markdown("### 📊 Prediction Results")
                        
                        # Create tabs for each position
                        tab1, tab2, tab3, tab4 = st.tabs(["🥅 Goalkeepers", "🛡️ Defenders", "⚽ Midfielders", "🎯 Forwards"])
                        
                        columns_to_hide = ['id_x', 'team', 'player_id']
                        
                        # Display predictions for each position
                        with tab1:
                            if 'goalkeepers' in position_dictionary:
                                df_display = position_dictionary['goalkeepers'].copy()
                                
                                # Calculate total_points based on selected gameweeks
                                gw_cols_to_sum = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                existing_gw_cols = [col for col in gw_cols_to_sum if col in df_display.columns]
                                if existing_gw_cols:
                                    df_display['total_points'] = df_display[existing_gw_cols].sum(axis=1)

                                # Remove unwanted columns if they exist
                                df_display = df_display.drop(columns=[col for col in columns_to_hide if col in df_display.columns])
                                
                                # Show top performers if points column exists
                                if 'total_points' in df_display.columns:
                                    # Sort by total points and show top 5
                                    df_sorted = df_display.sort_values(by='total_points', ascending=False)
                                    
                                    st.markdown("#### 🏆 Top 5 Goalkeepers")
                                    top_5 = df_sorted.head(5)
                                    
                                    for idx, (_, player) in enumerate(top_5.iterrows()):
                                        st.markdown(f"**#{idx+1} {player.iloc[0]}**")
                                        cols = st.columns(2 + (end_gw - start_gw + 1))
                                        cols[0].metric("Total Points", f"{player['total_points']:.1f}")
                                        if 'price' in df_display.columns:
                                            cols[1].metric("Price", f"£{player['price']:.1f}m")
                                        
                                        for i, gw in enumerate(range(start_gw, end_gw + 1)):
                                            gw_col = f"gw_{gw}"
                                            if gw_col in player:
                                                cols[i+2].metric(f"GW {gw}", f"{player[gw_col]:.1f}")
                                        st.markdown("---")

                                    st.markdown("#### 📊 All Goalkeepers")
                                    
                                    # Select columns to display
                                    cols_to_show = [df_sorted.columns[0]] # Player name
                                    if 'total_points' in df_sorted.columns:
                                        cols_to_show.append('total_points')
                                    if 'price' in df_sorted.columns:
                                        cols_to_show.append('price')
                                    
                                    gw_cols = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                    cols_to_show.extend([col for col in gw_cols if col in df_sorted.columns])
                                    
                                    st.dataframe(df_sorted[cols_to_show], use_container_width=True, hide_index=True)
                                else:
                                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        with tab2:
                            if 'defenders' in position_dictionary:
                                df_display = position_dictionary['defenders'].copy()

                                # Calculate total_points based on selected gameweeks
                                gw_cols_to_sum = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                existing_gw_cols = [col for col in gw_cols_to_sum if col in df_display.columns]
                                if existing_gw_cols:
                                    df_display['total_points'] = df_display[existing_gw_cols].sum(axis=1)

                                # Remove unwanted columns if they exist
                                df_display = df_display.drop(columns=[col for col in columns_to_hide if col in df_display.columns])
                                
                                # Show top performers if points column exists
                                if 'total_points' in df_display.columns:
                                    # Sort by total points and show top 5
                                    df_sorted = df_display.sort_values(by='total_points', ascending=False)
                                    
                                    st.markdown("#### 🏆 Top 5 Defenders")
                                    top_5 = df_sorted.head(5)
                                    
                                    for idx, (_, player) in enumerate(top_5.iterrows()):
                                        st.markdown(f"**#{idx+1} {player.iloc[0]}**")
                                        cols = st.columns(2 + (end_gw - start_gw + 1))
                                        cols[0].metric("Total Points", f"{player['total_points']:.1f}")
                                        if 'price' in df_display.columns:
                                            cols[1].metric("Price", f"£{player['price']:.1f}m")
                                        
                                        for i, gw in enumerate(range(start_gw, end_gw + 1)):
                                            gw_col = f"gw_{gw}"
                                            if gw_col in player:
                                                cols[i+2].metric(f"GW {gw}", f"{player[gw_col]:.1f}")
                                        st.markdown("---")
                                    
                                    st.markdown("#### 📊 All Defenders")
                                    
                                    # Select columns to display
                                    cols_to_show = [df_sorted.columns[0]] # Player name
                                    if 'total_points' in df_sorted.columns:
                                        cols_to_show.append('total_points')
                                    if 'price' in df_sorted.columns:
                                        cols_to_show.append('price')
                                    
                                    gw_cols = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                    cols_to_show.extend([col for col in gw_cols if col in df_sorted.columns])

                                    st.dataframe(df_sorted[cols_to_show], use_container_width=True, hide_index=True)
                                else:
                                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        with tab3:
                            if 'midfielders' in position_dictionary:
                                df_display = position_dictionary['midfielders'].copy()

                                # Calculate total_points based on selected gameweeks
                                gw_cols_to_sum = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                existing_gw_cols = [col for col in gw_cols_to_sum if col in df_display.columns]
                                if existing_gw_cols:
                                    df_display['total_points'] = df_display[existing_gw_cols].sum(axis=1)

                                # Remove unwanted columns if they exist
                                df_display = df_display.drop(columns=[col for col in columns_to_hide if col in df_display.columns])
                                
                                # Show top performers if points column exists
                                if 'total_points' in df_display.columns:
                                    # Sort by total points and show top 5
                                    df_sorted = df_display.sort_values(by='total_points', ascending=False)
                                    
                                    st.markdown("#### 🏆 Top 5 Midfielders")
                                    top_5 = df_sorted.head(5)
                                    
                                    for idx, (_, player) in enumerate(top_5.iterrows()):
                                        st.markdown(f"**#{idx+1} {player.iloc[0]}**")
                                        cols = st.columns(2 + (end_gw - start_gw + 1))
                                        cols[0].metric("Total Points", f"{player['total_points']:.1f}")
                                        if 'price' in df_display.columns:
                                            cols[1].metric("Price", f"£{player['price']:.1f}m")
                                        
                                        for i, gw in enumerate(range(start_gw, end_gw + 1)):
                                            gw_col = f"gw_{gw}"
                                            if gw_col in player:
                                                cols[i+2].metric(f"GW {gw}", f"{player[gw_col]:.1f}")
                                        st.markdown("---")
                                    
                                    st.markdown("#### 📊 All Midfielders")
                                    
                                    # Select columns to display
                                    cols_to_show = [df_sorted.columns[0]] # Player name
                                    if 'total_points' in df_sorted.columns:
                                        cols_to_show.append('total_points')
                                    if 'price' in df_sorted.columns:
                                        cols_to_show.append('price')
                                    
                                    gw_cols = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                    cols_to_show.extend([col for col in gw_cols if col in df_sorted.columns])

                                    st.dataframe(df_sorted[cols_to_show], use_container_width=True, hide_index=True)
                                else:
                                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        with tab4:
                            if 'forwards' in position_dictionary:
                                df_display = position_dictionary['forwards'].copy()

                                # Calculate total_points based on selected gameweeks
                                gw_cols_to_sum = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                existing_gw_cols = [col for col in gw_cols_to_sum if col in df_display.columns]
                                if existing_gw_cols:
                                    df_display['total_points'] = df_display[existing_gw_cols].sum(axis=1)

                                # Remove unwanted columns if they exist
                                df_display = df_display.drop(columns=[col for col in columns_to_hide if col in df_display.columns])
                                
                                # Show top performers if points column exists
                                if 'total_points' in df_display.columns:
                                    # Sort by total points and show top 5
                                    df_sorted = df_display.sort_values(by='total_points', ascending=False)
                                    
                                    st.markdown("#### 🏆 Top 5 Forwards")
                                    top_5 = df_sorted.head(5)
                                    
                                    for idx, (_, player) in enumerate(top_5.iterrows()):
                                        st.markdown(f"**#{idx+1} {player.iloc[0]}**")
                                        cols = st.columns(2 + (end_gw - start_gw + 1))
                                        cols[0].metric("Total Points", f"{player['total_points']:.1f}")
                                        if 'price' in df_display.columns:
                                            cols[1].metric("Price", f"£{player['price']:.1f}m")
                                        
                                        for i, gw in enumerate(range(start_gw, end_gw + 1)):
                                            gw_col = f"gw_{gw}"
                                            if gw_col in player:
                                                cols[i+2].metric(f"GW {gw}", f"{player[gw_col]:.1f}")
                                        st.markdown("---")
                                    
                                    st.markdown("#### 📊 All Forwards")
                                    
                                    # Select columns to display
                                    cols_to_show = [df_sorted.columns[0]] # Player name
                                    if 'total_points' in df_sorted.columns:
                                        cols_to_show.append('total_points')
                                    if 'price' in df_sorted.columns:
                                        cols_to_show.append('price')
                                    
                                    gw_cols = [f"gw_{gw}" for gw in range(start_gw, end_gw + 1)]
                                    cols_to_show.extend([col for col in gw_cols if col in df_sorted.columns])

                                    st.dataframe(df_sorted[cols_to_show], use_container_width=True, hide_index=True)
                                else:
                                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.error(f"❌ Error during prediction: {str(e)}")

# TAB 2: TEAM STATISTICS
with main_tab2:
    st.markdown("## 🏟️ Team Performance Analysis")
    
    # Team stats overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚽ Attacking Statistics")
        if not teams_stats_for.empty:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            
            # Sort by goals scored (descending)
            if len(teams_stats_for.columns) > 2:
                sorted_attacking = teams_stats_for.sort_values(by=teams_stats_for.columns[2], ascending=False)
            else:
                sorted_attacking = teams_stats_for
            
            # Top attacking teams
            st.markdown("#### 🔥 Top 5 Attacking Teams (by Goals Scored)")
            top_attacking = sorted_attacking.head(5)
            
            for idx, team in top_attacking.iterrows():
                col_team, col_goals, col_xg = st.columns([2, 1, 1])
                with col_team:
                    st.write(f"**{team.iloc[0]}**")  # Club name
                with col_goals:
                    st.metric("Goals", f"{team.iloc[2] if len(team) > 2 else 'N/A'}")
                with col_xg:
                    st.metric("xG", f"{float(team.iloc[5]):.1f}" if len(team) > 5 and pd.notna(team.iloc[5]) else "N/A")
            
            # Full attacking stats table (sorted)
            st.markdown("#### 📊 All Teams - Attacking Statistics")
            display_attacking = sorted_attacking.copy()
            
            # Round numeric columns
            numeric_cols = display_attacking.select_dtypes(include=['float64', 'int64']).columns
            display_attacking[numeric_cols] = display_attacking[numeric_cols].round(2)
            
            st.dataframe(display_attacking, use_container_width=True, hide_index=True)
            
            # Goals vs Expected Goals chart - ALL TEAMS
            if len(teams_stats_for.columns) > 5:
                fig = px.scatter(
                    sorted_attacking,
                    x=sorted_attacking.columns[5],  # Expected goals
                    y=sorted_attacking.columns[2],  # Goals scored
                    hover_name=sorted_attacking.columns[0],  # Club name
                    title="Goals Scored vs Expected Goals",
                    labels={sorted_attacking.columns[5]: "Expected Goals", 
                           sorted_attacking.columns[2]: "Goals Scored"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛡️ Defensive Statistics")
        if not teams_stats_against.empty:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            
            # Sort by goals conceded (ascending)
            if len(teams_stats_against.columns) > 2:
                sorted_defensive = teams_stats_against.sort_values(by=teams_stats_against.columns[2], ascending=True)
            else:
                sorted_defensive = teams_stats_against
            
            # Top defensive teams (fewest goals conceded)
            st.markdown("#### 🏆 Top 5 Defensive Teams (fewest Goals Conceded)")
            top_defensive = sorted_defensive.head(5)
            
            for idx, team in top_defensive.iterrows():
                col_team, col_goals, col_clean = st.columns([2, 1, 1])
                with col_team:
                    st.write(f"**{team.iloc[0]}**")  # Club name
                with col_goals:
                    st.metric("Goals Against", f"{team.iloc[2] if len(team) > 2 else 'N/A'}")
                with col_clean:
                    st.metric("Clean Sheets", f"{team.iloc[7] if len(team) > 7 else 'N/A'}")
            
            # Full defensive stats table (sorted)
            st.markdown("#### 📊 All Teams - Defensive Statistics")
            display_defensive = sorted_defensive.copy()
            
            # Round numeric columns
            numeric_cols = display_defensive.select_dtypes(include=['float64', 'int64']).columns
            display_defensive[numeric_cols] = display_defensive[numeric_cols].round(2)
            
            st.dataframe(display_defensive, use_container_width=True, hide_index=True)
            
            # Defensive performance chart - ALL TEAMS
            if len(teams_stats_against.columns) > 2:
                fig = px.bar(
                    sorted_defensive,
                    x=sorted_defensive.columns[0],  # Club name
                    y=sorted_defensive.columns[2],  # Goals conceded
                    title="Goals Conceded by Team (Sorted)",
                    labels={sorted_defensive.columns[0]: "Team", sorted_defensive.columns[2]: "Goals Conceded"}
                )
                fig.update_layout(
                    xaxis_tickangle=45,
                    xaxis_title="Team",
                    yaxis_title="Goals Conceded"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: PLAYER STATISTICS
with main_tab3:
    st.markdown("## 👤 Player Performance Analysis")
    
    # Position selector with updated titles and session state
    position_stats = {
        "Goalkeeping": goalkeepers_stats,
        "Defending": defenders_stats,
        "Passing": passing_stats,
        "Shooting": shooting_stats
    }
    
    # Initialize session state for player analysis selections
    if 'selected_position' not in st.session_state:
        st.session_state.selected_position = "Goalkeeping"
    if 'selected_feature' not in st.session_state:
        st.session_state.selected_feature = None
    if 'ascending_order' not in st.session_state:
        st.session_state.ascending_order = "Highest to Lowest"
    
    # Position selector with callback to update session state
    selected_position = st.selectbox(
        "Select Position", 
        list(position_stats.keys()),
        index=list(position_stats.keys()).index(st.session_state.selected_position),
        key="position_selectbox"
    )
    
    # Update session state when selection changes
    if selected_position != st.session_state.selected_position:
        st.session_state.selected_position = selected_position
        st.session_state.selected_feature = None  # Reset feature when position changes
    
    selected_df = position_stats[selected_position]
    
    if not selected_df.empty:
        # Get numeric columns for ranking (exclude player name and team columns)
        numeric_columns = []
        for i, col in enumerate(selected_df.columns):
            if i > 1:  # Skip first two columns (usually player name and team)
                try:
                    # Try to convert to numeric to see if it's a stat column
                    pd.to_numeric(selected_df[col], errors='raise')
                    numeric_columns.append(col)
                except:
                    pass
        
        if numeric_columns:
            # Set default feature if not set or if position changed
            if st.session_state.selected_feature is None or st.session_state.selected_feature not in numeric_columns:
                st.session_state.selected_feature = numeric_columns[0]
            
            # Feature selector for ranking
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📊 Rank Players by Feature")
                selected_feature = st.selectbox(
                    "Select statistic to rank by:", 
                    numeric_columns,
                    index=numeric_columns.index(st.session_state.selected_feature) if st.session_state.selected_feature in numeric_columns else 0,
                    help="Choose which statistic to use for ranking players",
                    key="feature_selectbox"
                )
                
                # Update session state
                st.session_state.selected_feature = selected_feature
            
            with col2:
                st.markdown("### 📈 Sort Order")
                ascending_order = st.radio(
                    "Ranking order:",
                    ["Highest to Lowest", "Lowest to Highest"],
                    index=0 if st.session_state.ascending_order == "Highest to Lowest" else 1,
                    help="Choose whether higher or lower values are better",
                    key="order_radio"
                )
                
                # Update session state
                st.session_state.ascending_order = ascending_order
                ascending = (ascending_order == "Lowest to Highest")
            
            # Sort by selected feature
            try:
                # Convert column to numeric for proper sorting
                display_df = selected_df.copy()
                display_df[selected_feature] = pd.to_numeric(display_df[selected_feature], errors='coerce')
                sorted_df = display_df.sort_values(by=selected_feature, ascending=ascending)
                
                # Main display area
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### 📊 {selected_position} Rankings")
                    st.markdown(f"*Sorted by {selected_feature} ({ascending_order.lower()})*")
                    
                    # Add ranking column
                    ranked_df = sorted_df.copy()
                    ranked_df.insert(0, 'Rank', range(1, len(ranked_df) + 1))
                    
                    # Round numeric columns
                    numeric_cols = ranked_df.select_dtypes(include=['float64', 'int64']).columns
                    ranked_df[numeric_cols] = ranked_df[numeric_cols].round(2)
                    
                    # Display the ranked table
                    st.dataframe(ranked_df, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown(f"### 🏆 Top 5 in {selected_feature}")
                    
                    # Show top 5 players
                    for i, (idx, player) in enumerate(sorted_df.head(5).iterrows()):
                        with st.container():
                            st.markdown(f"**#{i+1}**")
                            st.write(f"👤 {player.iloc[0] if len(player) > 0 else 'Unknown'}")
                            st.write(f"🏟️ {player.iloc[1] if len(player) > 1 else 'Unknown'}")
                            
                            # Show the selected feature value
                            feature_value = player[selected_feature]
                            if pd.notna(feature_value):
                                st.metric(selected_feature, f"{float(feature_value):.2f}")
                            else:
                                st.metric(selected_feature, "N/A")
                            
                            st.markdown("---")
                
                # Feature analysis chart
                st.markdown("---")
                st.markdown(f"### 📈 {selected_feature} Distribution")
                
                try:
                    # Create histogram of the selected feature
                    fig_hist = px.histogram(
                        sorted_df.head(20),
                        x=selected_feature,
                        title=f"{selected_feature} Distribution (Top 20 Players)",
                        labels={selected_feature: selected_feature}
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # Create bar chart of top performers
                    top_performers = sorted_df.head(10)
                    fig_bar = px.bar(
                        top_performers,
                        x=top_performers.columns[1],  # Player name
                        y=selected_feature,
                        title=f"Top 10 Players by {selected_feature}",
                        labels={top_performers.columns[1]: "Player", selected_feature: selected_feature}
                    )
                    fig_bar.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                except Exception as e:
                    st.warning(f"Could not create charts: {str(e)}")
                
                # Feature comparison
                st.markdown("---")
                st.markdown(f"### 📊 {selected_feature} Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                feature_data = pd.to_numeric(sorted_df[selected_feature], errors='coerce').dropna()
                if not feature_data.empty:
                    with col1:
                        st.metric("Average", f"{feature_data.mean():.2f}")
                    with col2:
                        st.metric("Median", f"{feature_data.median():.2f}")
                    with col3:
                        st.metric("Max", f"{feature_data.max():.2f}")
                    with col4:
                        st.metric("Min", f"{feature_data.min():.2f}")
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
                st.dataframe(selected_df, use_container_width=True, hide_index=True)
        
        else:
            st.warning("No numeric columns found for ranking. Displaying raw data.")
            st.dataframe(selected_df, use_container_width=True, hide_index=True)
    
    # Player search functionality
    st.markdown("---")
    st.markdown("### 🔍 Player Search & Analysis")
    
    # Combine all player data for search
    all_players = pd.DataFrame()
    for pos_name, df in position_stats.items():
        if not df.empty:
            df_copy = df.copy()
            df_copy['Position'] = pos_name
            all_players = pd.concat([all_players, df_copy], ignore_index=True)
    
    if not all_players.empty:
        # Player search
        player_search = st.text_input("🔍 Search for a player", placeholder="Type player name...")
        
        if player_search:
            # Filter players based on search
            mask = all_players.iloc[:, 0].str.contains(player_search, case=False, na=False)
            filtered_players = all_players[mask]
            
            if not filtered_players.empty:
                st.markdown(f"### Search Results for '{player_search}' ({len(filtered_players)} found)")
                
                # Display search results
                for idx, player in filtered_players.head(10).iterrows():
                    with st.expander(f"👤 {player.iloc[0]} - {player['Position']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Team:** {player.iloc[1] if len(player) > 1 else 'Unknown'}")
                            st.write(f"**Position:** {player['Position']}")
                        
                        with col2:
                            # Show all numeric stats for this player
                            for col_name in player.index:
                                if col_name not in ['Position'] and pd.api.types.is_numeric_dtype(type(player[col_name])):
                                    try:
                                        value = float(player[col_name])
                                        st.metric(col_name, f"{value:.2f}")
                                    except:
                                        continue
            else:
                st.warning(f"No players found matching '{player_search}'")

# TAB 4: DREAM TEAM
with main_tab4:
    st.markdown("## ⭐ Dream Team Selection")
    st.markdown(f"### 🌟 Optimal Squad for Gameweek {finished_gw + 1} Based on Predicted Points")
    
    if position_dictionary:
        dream_team_result = create_dream_team(position_dictionary, finished_gw)
        
        if dream_team_result:
            starting_xi = dream_team_result['starting_xi']
            substitutes = dream_team_result['substitutes']
            dream_team = dream_team_result['dream_team']
            points_col = dream_team_result['points_col']
            
            # Display Dream Team
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 🏆 Starting XI")
                st.markdown("*Formation: Optimal based on predicted points*")
                
                # Captain and Vice Captain
                if len(starting_xi) >= 2:
                    captain = starting_xi[0]
                    vice_captain = starting_xi[1]
                    
                    col_cap, col_vice = st.columns(2)
                    with col_cap:
                        st.markdown("#### 👑 Captain")
                        st.success(f"**{captain.get('web_name', 'Unknown')}** ({captain['position']})")
                        st.metric(f"Predicted GW {finished_gw + 1} Points", f"{captain[points_col]:.1f}")
                    
                    with col_vice:
                        st.markdown("#### 🎖️ Vice Captain")
                        st.info(f"**{vice_captain.get('web_name', 'Unknown')}** ({vice_captain['position']})")
                        st.metric(f"Predicted GW {finished_gw + 1} Points", f"{vice_captain[points_col]:.1f}")
                
                # Starting XI table
                starting_xi_df = pd.DataFrame([
                    {
                        'Player': player.get('web_name', 'Unknown'),
                        'Position': player['position'],
                        f'Predicted GW {finished_gw + 1} Points': f"{player[points_col]:.1f}",
                        'Role': '👑 Captain' if i == 0 else '🎖️ Vice Captain' if i == 1 else '⚽ Player'
                    }
                    for i, player in enumerate(starting_xi)
                ])
                
                # Sort by position for display
                position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
                starting_xi_df['Position'] = pd.Categorical(starting_xi_df['Position'], categories=position_order, ordered=True)
                starting_xi_df = starting_xi_df.sort_values('Position')

                st.dataframe(starting_xi_df, use_container_width=True, hide_index=True)
                
            with col2:
                st.markdown("### 🔄 Substitutes Bench")
                
                if substitutes:
                    for i, player in enumerate(substitutes):
                        with st.container():
                            st.markdown(f"**Sub {i+1}: {player.get('web_name', 'Unknown')}**")
                            st.write(f"Position: {player['position']}")
                            st.metric(f"GW {finished_gw + 1} Points", f"{player[points_col]:.1f}", label_visibility="collapsed")
                            st.markdown("---")
                else:
                    st.info("No substitutes available")
                
                # Squad summary
                st.markdown("### 📊 Squad Summary")
                
                # Count positions in starting XI
                position_counts = {}
                for player in starting_xi:
                    pos = player['position']
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                
                for pos, count in position_counts.items():
                    st.metric(f"{pos}s", count)
            
            # Formation visualization
            st.markdown("---")
            st.markdown("### ⚽ Formation Breakdown")
            
            formation_col1, formation_col2, formation_col3, formation_col4 = st.columns(4)
            
            # Group players by position for formation display
            formation_players = {
                'Goalkeeper': [p for p in starting_xi if p['position'] == 'Goalkeeper'],
                'Defender': [p for p in starting_xi if p['position'] == 'Defender'],
                'Midfielder': [p for p in starting_xi if p['position'] == 'Midfielder'],
                'Forward': [p for p in starting_xi if p['position'] == 'Forward']
            }
            
            with formation_col1:
                st.markdown("#### 🥅 GK")
                for player in formation_players['Goalkeeper']:
                    role = '👑' if player[points_col] == starting_xi[0][points_col] else '🎖️' if len(starting_xi) > 1 and player[points_col] == starting_xi[1][points_col] else ''
                    st.write(f"{role} {player.get('web_name', 'Unknown')}")
            
            with formation_col2:
                st.markdown("#### 🛡️ DEF")
                for player in formation_players['Defender']:
                    role = '👑' if player[points_col] == starting_xi[0][points_col] else '🎖️' if len(starting_xi) > 1 and player[points_col] == starting_xi[1][points_col] else ''
                    st.write(f"{role} {player.get('web_name', 'Unknown')}")
            
            with formation_col3:
                st.markdown("#### ⚽ MID")
                for player in formation_players['Midfielder']:
                    role = '👑' if player[points_col] == starting_xi[0][points_col] else '🎖️' if len(starting_xi) > 1 and player[points_col] == starting_xi[1][points_col] else ''
                    st.write(f"{role} {player.get('web_name', 'Unknown')}")
            
            with formation_col4:
                st.markdown("#### 🎯 FWD")
                for player in formation_players['Forward']:
                    role = '👑' if player[points_col] == starting_xi[0][points_col] else '🎖️' if len(starting_xi) > 1 and player[points_col] == starting_xi[1][points_col] else ''
                    st.write(f"{role} {player.get('web_name', 'Unknown')}")
        
        else:
            st.warning("Unable to create Dream Team.")
            if not all(pos in position_dictionary for pos in ['goalkeepers', 'defenders', 'midfielders', 'forwards']):
                missing_positions = [pos for pos in ['goalkeepers', 'defenders', 'midfielders', 'forwards'] if pos not in position_dictionary]
                st.info(f"Missing data for: {', '.join(missing_positions)}")
            else:
                st.info(f"Please ensure predictions have been generated with a '{f'gw_{finished_gw + 1}'}' column.")
    
    else:
        st.warning("No prediction data available.")
        st.info("Please go to the Predictions tab and generate predictions first to create your Dream Team!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; padding: 20px;'>
        <p>Fantasy Premier League Predictor v2.0 | Built with ❤️ and Streamlit</p>
        <p>⚽ Good luck with your Fantasy team! ⚽</p>
    </div>
    """, 
    unsafe_allow_html=True
)