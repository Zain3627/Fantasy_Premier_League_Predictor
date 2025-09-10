import pandas as pd
import numpy as np
from datetime import datetime, timezone

class DataPreprocessing:
    def __init__(self):
        pass
    
    def fixtures_processing(self,df):
        cols = ['finished_provisional','kickoff_time','minutes','provisional_start_time','started','team_a_score','team_h_score']
        df = df.drop(columns=cols)
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
    
    # def midfielder_preprocessing(self,df):
    #     cols = ['kickoff_time']
    #     df = df.drop(columns=cols)
    #     return df
    
    # def forward_preprocessing(self,df):
    #     cols = ['kickoff_time']
    #     df = df.drop(columns=cols)
    #     return df
