import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import altair as alt
from extensions.collect_data import get_bowler_data

if pd.read_pickle('lastsave.pkl').strftime("%Y-%m-%d") != datetime.today().strftime("%Y-%m-%d"):
    get_bowler_data()
    pd.to_pickle(datetime.today(), 'lastsave.pkl')

data = pd.read_pickle('scraped_bowler_data.pkl')

# Streamlit App

date1 = pd.to_datetime(st.sidebar.date_input("Start Date", data.date.min()))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", data.date.max()))

selected_season = st.sidebar.multiselect(
    'Season', 
    np.append(data['season'].unique(), ["All"]), 
    default="All"
    )

if "All" in selected_season:
    selected_season = data['season'].unique()
    
selected_pair = st.sidebar.multiselect(
    'Lane Assignment',
    np.append(data['lane_pair'].unique(), ['All']),
    default='All'
)

if "All" in selected_pair:
    selected_pair = data['lane_pair'].unique()

data_filtered = data[
    data.season.isin(selected_season) &
    data.lane_pair.isin(selected_pair) &
    (data.date >= date1) &
    (data.date <= date2)
]

# Calculate key metrics overall
total_games = len(data.score)
high_game = data.score.max()
high_series = data.total.max()
total_pins = data.score.sum()
average = round(total_pins / total_games, 2)
# Calculate key metrics filtered
total_games_filtered = len(data_filtered.score)
high_game_filtered = data_filtered.score.max()
high_series_filtered = data_filtered.total.max()
total_pins_filtered = data_filtered.score.sum()
average_filtered = round(total_pins_filtered / total_games_filtered, 2)

low_game_filtered = data_filtered.score.min()
low_series_filtered = data_filtered.total.min()

# Overall Statistics
st.header('Overall Statistics')
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

metric_col1.metric(label='Overall Average', value=average)
metric_col2.metric(label='Total Games', value=total_games)
metric_col3.metric(label='High Series', value=high_series)
metric_col4.metric(label='High Game', value=high_game)

st.header("", divider='blue')

# Filtered Statistics
st.subheader('vs. Filtered Statistics')
filmet_col1, filmet_col2, filmet_col3, filmet_col4 = st.columns(4)

filmet_col1.metric(
    label='Filtered Average', 
    value=average_filtered, 
    delta=f"{round(average_filtered - average, 1)} pins"
)
filmet_col2.metric(
    label = 'Total Games',
    value = total_games_filtered,
    delta = f"{total_games_filtered - total_games} games"
)
filmet_col3.metric(
    label = 'High Series',
    value = high_series_filtered,
    delta = f"{high_series_filtered - high_series}"
)
filmet_col4.metric(
    label = 'High Game',
    value = high_game_filtered,
    delta = high_game_filtered - high_game
)

st.header("", divider='blue')

tab1, tab2, tab3 = st.tabs(['data', 'graphs', 'analysis'])

with tab1:
    st.subheader('Filtered Data')
    st.dataframe(
        data_filtered \
            .pivot(index=['date', 'week', 'season', 'total', 'lane_pair'], 
                columns='game', values='score') \
            .reset_index() \
            .loc[:, ['date', 'season', 'week', 'game1', 'game2', 'game3', 'total', 'lane_pair']] \
            .sort_values('date', ascending=False), 
        hide_index=True,
        height=1000
        
    )

with tab2:
    
    st.subheader("Graphs")
    col1, col2, col3 = st.columns(3)
    
    col1.write(
        alt.Chart(data=data_filtered[['game', 'score']] \
            .groupby('game') \
            .mean() \
            .reset_index(),
            title = "Average by Game"       
            ) \
        .mark_bar(color= 'green') \
        .encode(
            alt.X('game', title = ''), 
            alt.Y('score', title='Average')        
        )
            
    )
    
    col2.write(
        alt.Chart(
            data=data_filtered[['season', 'score']] \
            .groupby('season') \
            .mean() \
            .reset_index(),
            title = "Average by Season"       
        ) \
        .mark_bar(color= 'green') \
        .encode(
            x = alt.X('season', title = ''), 
            y = alt.Y('score', title='Average')        
        )
            
    )
    
    col3.write(
        alt.Chart(data=data_filtered[['lane_pair', 'score']] \
            .groupby('lane_pair') \
            .mean() \
            .reset_index(),
            title = 'Average by Lane'       
            ) \
        .mark_bar(color= 'green') \
        .encode(
            alt.X(
                'lane_pair',
                title = '', 
                sort= '-y'
                ), 
            alt.Y('score', title = 'Average')        
        )
            
    )
    
    col1.write(
        alt.Chart(
            data = data_filtered[['date', 'score']],
            title = "Game Distribution") \
        .mark_bar(color = 'green') \
        .encode(
            x = alt.X('score', bin = alt.BinParams(maxbins=10)), 
            y = 'count()')
    )
    
    col1.write(
        alt.Chart(
            data = data_filtered[['date', 'total']].drop_duplicates(),
            title = "Series Distribution"
        ) \
        .mark_bar(color = 'green') \
        .encode(
            x = alt.X('total', bin=alt.BinParams(maxbins=10)), 
            y = 'count()')
    )   
      
with tab3:
        # header_col1, header_col2 = st.columns(2)
# header_col1.header("Overall Statistics")
# header_col1.write(f"High Game: {high_game} bowled on {data[(data.score == high_game)].date.to_string(index=False)}")

# header_col1.write(f"High Series: {high_series} bowled on {data[['date', 'total']][(data.total == high_series)].drop_duplicates().date.to_string(index=False)}")
    
    st.write(f"High Game: {high_game_filtered} bowled on {data_filtered[(data_filtered.score == high_game_filtered)].date.to_string(index=False)}")
    st.write(f"High Series: {high_series_filtered} bowled on {data_filtered[['date', 'total']][(data_filtered.total == high_series_filtered)].drop_duplicates().date.to_string(index=False)}")
    
    st.write(f"Low Game: {low_game_filtered} bowled on {data_filtered[(data_filtered.score == low_game_filtered)].date.to_string(index=False)}")
    st.write(f"Low Series: {low_series_filtered} bowled on {data_filtered[['date', 'total']][(data_filtered.total == low_series_filtered)].drop_duplicates().date.to_string(index=False)}")
    
    col1, col2, col3 = st.columns(3)
    
    # Best Season
    col1.write("Best Season")
    col1.dataframe(data[['season', 'score']] \
        .groupby('season') \
        .mean() \
        .query("score == score.max()") \
        .rename(columns = {'score':'Average'}) \
        .rename_axis(index='Best Season', columns = None) \
        .reset_index(),
        hide_index= True
    )
    
    # Worst Season
    col1.write("Worst Season")
    col1.dataframe(data[['season', 'score']] \
        .groupby('season') \
        .mean() \
        .query("score == score.min()") \
        .rename(columns = {'score':'Average'}) \
        .rename_axis(index='Worst Season', columns = None) \
        .reset_index(),
        hide_index=True
    
    )
    # Best Lane Assignment
    col2.write("Best Lane")
    col2.dataframe(data[['lane_pair', 'score']] \
        .groupby('lane_pair') \
        .mean() \
        .query("score == score.max()") \
        .rename(columns = {'score':'Average'}) \
        .rename_axis(index='Lane Assignment', columns = None) \
        .reset_index(),
        hide_index= True
    )
    # Worst Lane Assignment
    col2.write("Worst Lane")
    col2.dataframe(data[['lane_pair', 'score']] \
        .groupby('lane_pair') \
        .mean() \
        .query("score == score.min()") \
        .rename(columns = {'score':'Average'}) \
        .rename_axis(index = 'Lane Assignment') \
        .reset_index(),
        hide_index=True
    )
    
    col3.write("Best Month")
    col3.dataframe(data[['date', 'score']] \
        .set_index('date') \
        .resample('M') \
        .mean() \
        .query("score == score.max()") \
        .reset_index() \
        .assign(date = lambda x: x.date.dt.strftime("%m-%Y")),
        hide_index=True
    )
    
    # Worst Month
    col3.write("Worst Month")
    col3.dataframe(data[['date', 'score']] \
        .set_index('date') \
        .resample('M') \
        .mean() \
        .query("score == score.min()") \
        .reset_index() \
        .assign(date = lambda x: x.date.dt.strftime("%m-%Y")),
        hide_index=True
    )