import streamlit as st
import DataLoader as dl
import DataPreprocessing as dp
import FantasyPredicorPipeline as fpp
import FantasyModel as fm
import FeatureEngineering as fe
import pandas as pd
import time

# Configure page
st.set_page_config(
    page_title="Fantasy Premier League Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_initialized' not in st.session_state:
    st.session_state.pipeline_initialized = False
    st.session_state.pipeline = None

# Title and header
st.markdown('<h1 class="title">⚽ Fantasy Premier League Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Predict player performance for upcoming gameweeks using advanced machine learning</p>', unsafe_allow_html=True)

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
    1. Enter the start gameweek
    2. Enter the end gameweek
    3. Click 'Generate Predictions'
    4. Wait for results to download
    """)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🔢 Select Gameweeks")
    
    # Input fields
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        start_gw = st.number_input(
            "Start Gameweek",
            min_value=1,
            max_value=38,
            value=4,
            help="Enter the starting gameweek number (1-38)"
        )
    
    with col_input2:
        end_gw = st.number_input(
            "End Gameweek", 
            min_value=1,
            max_value=38,
            value=6,
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
                # Initialize the pipeline if not already done
                if not st.session_state.pipeline_initialized:
                    try:
                        loader = dl.DataLoader()
                        preprocessor = dp.DataPreprocessing()
                        goalkeeper_model = fm.FantasyModel(1)
                        defender_model = fm.FantasyModel(2)
                        attacker_model = fm.FantasyModel(3)
                        feature_engineering = fe.FeatureEngineering()
                        
                        st.session_state.pipeline = fpp.FantasyPredicorPipeline(
                            loader, preprocessor, goalkeeper_model, 
                            defender_model, attacker_model, feature_engineering
                        )
                        st.session_state.pipeline_initialized = True
                        
                        st.success("✅ Pipeline initialized successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error initializing pipeline: {str(e)}")
                        st.stop()
            
            # Run predictions
            with st.spinner(f'🎯 Generating predictions for gameweeks {start_gw} to {end_gw}. This may take a few minutes...'):
                try:
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Run the actual prediction
                    position_dictionary = st.session_state.pipeline.run(start_gw, end_gw)
                    # Update progress
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
                        time.sleep(0.02)  # Small delay for visual effect
                    
                    
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Success message
                    st.success(f"🎉 Predictions generated successfully for gameweeks {start_gw} to {end_gw}!")
                    
                    # Display results for each position
                    st.markdown("### � Prediction Results")
                    
                    # Create tabs for each position
                    tab1, tab2, tab3, tab4 = st.tabs(["🥅 Goalkeepers", "🛡️ Defenders", "⚽ Midfielders", "🎯 Forwards"])
                    
                    # Goalkeepers tab
                    with tab1:
                        if 'goalkeepers' in position_dictionary:
                            gk_df = position_dictionary['goalkeepers']
                            st.markdown("#### Top 10 Goalkeepers")
                            
                            # Display key columns with proper formatting
                            display_cols = ['web_name', 'name'] + [col for col in gk_df.columns if col.startswith('gw_')] + ['total_points']
                            display_df = gk_df[display_cols].head(10).copy()
                            
                            # Round numeric columns to 2 decimal places
                            numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
                            display_df[numeric_cols] = display_df[numeric_cols].round(2)
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # Show top 3 as metrics
                            st.markdown("#### 🏆 Top 3 Picks")
                            col1, col2, col3 = st.columns(3)
                            for i, (idx, player) in enumerate(gk_df.head(3).iterrows()):
                                with [col1, col2, col3][i]:
                                    st.metric(
                                        label=f"#{i+1}",
                                        value=f"{player['web_name']}",
                                        delta=f"{player['total_points']:.2f} pts"
                                    )
                    
                    # Defenders tab
                    with tab2:
                        if 'defenders' in position_dictionary:
                            def_df = position_dictionary['defenders']
                            st.markdown("#### Top 15 Defenders")
                            
                            # Display key columns with proper formatting
                            display_cols = ['web_name', 'name'] + [col for col in def_df.columns if col.startswith('gw_')] + ['total_points']
                            display_df = def_df[display_cols].head(15).copy()
                            
                            # Round numeric columns to 2 decimal places
                            numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
                            display_df[numeric_cols] = display_df[numeric_cols].round(2)
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # Show top 5 as metrics
                            st.markdown("#### 🏆 Top 5 Picks")
                            cols = st.columns(5)
                            for i, (idx, player) in enumerate(def_df.head(5).iterrows()):
                                with cols[i]:
                                    st.metric(
                                        label=f"#{i+1}",
                                        value=f"{player['web_name']}",
                                        delta=f"{player['total_points']:.2f} pts"
                                    )
                    
                    # Midfielders tab
                    with tab3:
                        if 'midfielders' in position_dictionary:
                            mid_df = position_dictionary['midfielders']
                            st.markdown("#### Top 15 Midfielders")
                            
                            # Display key columns with proper formatting
                            display_cols = ['web_name', 'name'] + [col for col in mid_df.columns if col.startswith('gw_')] + ['total_points']
                            display_df = mid_df[display_cols].head(15).copy()
                            
                            # Round numeric columns to 2 decimal places
                            numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
                            display_df[numeric_cols] = display_df[numeric_cols].round(2)
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # Show top 5 as metrics
                            st.markdown("#### 🏆 Top 5 Picks")
                            cols = st.columns(5)
                            for i, (idx, player) in enumerate(mid_df.head(5).iterrows()):
                                with cols[i]:
                                    st.metric(
                                        label=f"#{i+1}",
                                        value=f"{player['web_name']}",
                                        delta=f"{player['total_points']:.2f} pts"
                                    )
                    
                    # Forwards tab
                    with tab4:
                        if 'forwards' in position_dictionary:
                            fwd_df = position_dictionary['forwards']
                            st.markdown("#### Top 10 Forwards")
                            
                            # Display key columns with proper formatting
                            display_cols = ['web_name', 'name'] + [col for col in fwd_df.columns if col.startswith('gw_')] + ['total_points']
                            display_df = fwd_df[display_cols].head(10).copy()
                            
                            # Round numeric columns to 2 decimal places
                            numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
                            display_df[numeric_cols] = display_df[numeric_cols].round(2)
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # Show top 3 as metrics
                            st.markdown("#### 🏆 Top 3 Picks")
                            col1, col2, col3 = st.columns(3)
                            for i, (idx, player) in enumerate(fwd_df.head(3).iterrows()):
                                with [col1, col2, col3][i]:
                                    st.metric(
                                        label=f"#{i+1}",
                                        value=f"{player['web_name']}",
                                        delta=f"{player['total_points']:.2f} pts"
                                    )
                    
                except Exception as e:
                    st.error(f"❌ Error during prediction: {str(e)}")
                    st.markdown("Please check your input parameters and try again.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; padding: 20px;'>
        <p>Fantasy Premier League Predictor v1.0 | Built with ❤️ and Streamlit</p>
        <p>⚽ Good luck with your Fantasy team! ⚽</p>
    </div>
    """, 
    unsafe_allow_html=True
)
