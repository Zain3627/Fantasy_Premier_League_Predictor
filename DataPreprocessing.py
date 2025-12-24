import pandas as pd
from datetime import datetime, timezone

class DataPreprocessing:
    def __init__(self):
        pass
    
    import pandas as pd

    def fixtures_processing(self, fixtures):

        if isinstance(fixtures, dict):
            if 'fixtures' in fixtures:
                fixtures = fixtures['fixtures']
            else:
                fixtures = next(v for v in fixtures.values() if isinstance(v, list))

        # Now fixtures is a list of dicts
        df = pd.DataFrame.from_records(fixtures)
        cols_to_drop = [
            'finished_provisional',
            'kickoff_time',
            'minutes',
            'provisional_start_time',
            'started',
            'team_a_score',
            'team_h_score'
        ]

        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
        return df


    def get_current_gw(self,df):
        df['deadline_time'] = pd.to_datetime(df['deadline_time'], utc=True)
        now = datetime.now(timezone.utc)
        upcoming_gw = df[df['deadline_time'] > now].iloc[0]
        return upcoming_gw['id']

    def teams_processing(self, df):
        cols = ['draw','form','loss','played','points','team_division','unavailable','win','pulse_id','code']
        df = df.drop(columns=cols)
        return df

    def players_processing(self, df):
        cols = ['can_transact','can_select','code','cost_change_event','cost_change_event_fall','cost_change_start','cost_change_start_fall','in_dreamteam','news','news_added','photo',
                'transfers_in','transfers_in_event','transfers_out','transfers_out_event','region','team_join_date','birth_date','has_temporary_code','opta_code','value_season',
                'now_cost_rank','now_cost_rank_type','form_rank','form_rank_type','points_per_game_rank','points_per_game_rank_type','selected_rank','selected_rank_type',
                'removed','special','squad_number','direct_freekicks_text','penalties_text','corners_and_indirect_freekicks_text','chance_of_playing_this_round','value_form',
                'influence_rank','influence_rank_type','creativity_rank','creativity_rank_type','threat_rank','threat_rank_type','ict_index_rank','ict_index_rank_type',
                'now_cost','first_name','second_name','selected_by_percent','own_goals','dreamteam_count','total_points','ep_this' , 'ep_next']
        df = df.drop(columns=cols)
        df['chance_of_playing_next_round'] = df['chance_of_playing_next_round'].fillna(100)

        df['direct_freekicks_order'] = df['direct_freekicks_order'].fillna(0)
        df['corners_and_indirect_freekicks_order'] = df['corners_and_indirect_freekicks_order'].fillna(0)
        df['penalties_order'] = df['penalties_order'].fillna(0)

        def is_ready(row):
            # Status hard rules
            if row['status'] in ['u','i','s','n']:
                return 0
            elif row['chance_of_playing_next_round'] <= 50:
                return 0
            elif row['status'] == 'a' and row['chance_of_playing_next_round'] >= 75:
                return 1
            
            
        def will_start(row):
            # Now refine with historical performance
            if row['ready'] == 1:
                if row['starts'] == 0:
                    return 0
                elif row['minutes'] >= row['starts'] * 70:
                    return 1
                else:
                    return 0.7
            else:
                return 0
        
        df['ready'] = df.apply(is_ready,axis=1)
        df['will_play'] = df.apply(will_start,axis=1)
        cols = ['ready','starts_per_90','minutes','chance_of_playing_next_round']
        df = df.drop(columns=cols)

        df = df[['element_type','id','web_name','team','points_per_game','will_play']]
        return df
        
    def divide_by_position(self,df):
        goalkeepers = df[df['element_type']==1]
        goalkeepers = self.goalkeeper_preprocessing(goalkeepers)
        defenders = df[df['element_type']==2]
        defenders = self.players_preprocessing(defenders)
        midfielders = df[df['element_type']==3]
        midfielders = self.players_preprocessing(midfielders)
        forwards = df[df['element_type']==4]
        forwards = self.players_preprocessing(forwards)

        return df,goalkeepers,defenders,midfielders,forwards

    def goalkeeper_preprocessing(self,df):
        cols = ['kickoff_time','modified','defensive_contribution','value','transfers_balance','selected','transfers_in','transfers_out','penalties_missed','tackles']
        df = df.drop(columns=cols)
        return df
    
    def players_preprocessing(self,df):
        cols = ['kickoff_time','modified','saves','value','transfers_balance','selected','transfers_in','transfers_out','penalties_saved']
        df = df.drop(columns=cols)
        return df
    
    def stats_teams_prepocessing(self,df, f_a):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

        cols_drop = ['Unnamed: 1_level_0_# Pl','Unnamed: 2_level_0_Age','Playing Time_MP','Playing Time_Starts','Playing Time_Min','Playing Time_90s',
                     'Performance_CrdY','Performance_CrdR','Expected_npxG','Expected_npxG+xAG','Progression_PrgC','Progression_PrgP','Performance_Ast','Performance_G+A','Performance_PK',
                     'Expected_xAG','Per 90 Minutes_Ast','Per 90 Minutes_G+A','Per 90 Minutes_xAG','Per 90 Minutes_xG+xAG',
                     'Per 90 Minutes_G-PK','Per 90 Minutes_G+A-PK','Per 90 Minutes_npxG','Per 90 Minutes_npxG+xAG']
        df.drop(columns=cols_drop,inplace=True)
        if not f_a:
            df.columns = ['Club','Possession','Goals scored','Non-penalty goals','Penalties','Expected goals','Goals permatch','Expected goals per match']
        else:
            df.columns = ['Club','Possession against','Goals against (no OG)','Non-penalty goals','Penalties against','Expected goals against','Goals permatch against',
                          'Expected goals per match against']

        return df
    
    def stats_gk_preprocessing(self,df):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 0] != 'Rk'].reset_index(drop=True) if df is not None and not df.empty else df

        cols_drop = ['Unnamed: 0_level_0_Rk','Unnamed: 2_level_0_Nation','Unnamed: 3_level_0_Pos','Unnamed: 5_level_0_Age','Unnamed: 6_level_0_Born',
                     'Playing Time_MP','Playing Time_Starts','Playing Time_Min','Playing Time_90s','Performance_W','Performance_D','Performance_L',
                     'Penalty Kicks_PKatt','Penalty Kicks_PKA','Penalty Kicks_PKm','Penalty Kicks_Save%','Unnamed: 26_level_0_Matches']
        df.drop(columns=cols_drop,inplace=True)

        df.columns = ['Player','Team','Goals against', 'Goals against per match', 'Shots against', 'Saves', 'Save %', 'Clean sheets', 'Clean sheets per match', 'Penalties saved']
        return df
    
    def stats_defence_preprocessing(self,df):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 0] != 'Rk'].reset_index(drop=True) if df is not None and not df.empty else df
        cols_drop = ['Unnamed: 0_level_0_Rk','Unnamed: 2_level_0_Nation','Unnamed: 3_level_0_Pos','Unnamed: 5_level_0_Age','Unnamed: 6_level_0_Born','Unnamed: 7_level_0_90s',
                     'Tackles_Def 3rd','Tackles_Mid 3rd','Tackles_Att 3rd','Challenges_Tkl','Challenges_Att','Challenges_Tkl%','Challenges_Lost','Blocks_Sh','Blocks_Pass',
                     'Unnamed: 21_level_0_Tkl+Int','Unnamed: 24_level_0_Matches']
        df.drop(columns=cols_drop,inplace=True)

        df.columns = ['Player','Team','Tackles', 'Tackles won', 'Blocks', 'Interceptions', 'Clearences', 'Errors leading to shots']

        return df
    
    def stats_passing_preprocessing(self,df):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 0] != 'Rk'].reset_index(drop=True) if df is not None and not df.empty else df

        df = df[['Unnamed: 1_level_0_Player', 'Unnamed: 4_level_0_Squad', 'Total_Cmp','Total_Cmp%','Unnamed: 22_level_0_Ast','Expected_xA','Unnamed: 26_level_0_KP']]

        df.columns = ['Player','Team','Passes completed','Passes completed %','Assists','Expected assists','Key passes']
        
        return df
    
    def stats_shooting_preprocessing(self,df):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 0] != 'Rk'].reset_index(drop=True) if df is not None and not df.empty else df

        cols_drop = ['Unnamed: 0_level_0_Rk','Unnamed: 2_level_0_Nation','Unnamed: 3_level_0_Pos','Unnamed: 5_level_0_Age','Unnamed: 6_level_0_Born','Unnamed: 7_level_0_90s',
                     'Standard_Dist','Standard_G/SoT', 'Standard_PKatt','Expected_npxG','Expected_npxG/Sh', 'Expected_G-xG', 'Expected_np:G-xG', 'Unnamed: 25_level_0_Matches']
        df.drop(columns=cols_drop,inplace=True)

        df.columns = ['Player','Team','Goals','Shots', 'Shots on target', 'Shots on target %', 'Shots per match', 'Shots on target per match', 'Goal per shot', 'Fouls scored',
                      'Penalties scored', 'Expected goals']

        return df
    