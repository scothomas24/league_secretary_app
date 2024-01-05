import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_bowler_data(bowler_name = "scott-thomas"):

    data = pd.DataFrame(columns=['week', 'date', 'game1', 'game2', 'game3', 'total'])
    years = [2021, 2022, 2023]

    for year in years:
        url = f"https://www.leaguesecretary.com/bowling-centers/harbor-lanes-saint-clair-shores-michigan/bowling-leagues/lochmoor-men-2324/bowler-info/scott-thomas/{year}/fall/117119/60"

        html = pd.read_html(url, flavor='html5lib')
        
        df = pd.DataFrame(np.array([html])[0,0,:-1,:6],
        columns=['week', 'date', 'game1', 'game2', 'game3', 'total']
        ) \
        .query('total != 0')
        
        data = pd.concat([data, df])

    # Pivot Longer
    data = data \
        .melt(
            value_vars = ['game1', 'game2', 'game3'],
            var_name = 'game',
            value_name = 'score',
            id_vars = ['week', 'date', 'total']
        )[['week', 'date', 'game', 'score', 'total']]

    # #Find name in URL
    # name = url[url.find('bowler-info/') + len('bowler-info/'): url.rfind('/20')]

    #convert data types
    data[['week', 'score', 'total']] = data \
        [['week', 'score', 'total']] \
        .apply(lambda x: x.astype('int'))

    data['date'] = data['date'].apply(lambda x: pd.to_datetime(x))

    # Add Season Column
    def calc_season(date):
        if date > pd.to_datetime("2021-09-01") and date < pd.to_datetime("2022-06-01"):
            return '2021-2022'
        elif date > pd.to_datetime("2022-09-01") and date < pd.to_datetime("2023-06-01"):
            return '2022-2023'
        elif date > pd.to_datetime("2023-09-01") and date < pd.to_datetime("2024-06-01"):
            return '2023-2024'

    data['season'] = data['date'].apply(lambda x: calc_season(x))

    #scrape and collect lane assignment data from team history
    la_data = pd.DataFrame(columns=['week', 'date', 'lanes'])

    years_and_page = [(2021,1), (2021,2), (2022,1), (2022,2), (2023,1), (2023,2)]

    for (year, page) in years_and_page:
        la_url = f"https://www.leaguesecretary.com/bowling-centers/harbor-lanes-saint-clair-shores-michigan/bowling-leagues/lochmoor-men-2324/team/history/12-team-thomas/{year}/Fall/117119/12/{page}"
        la_html = pd.read_html(la_url)
        
        la_df = pd.DataFrame(
            np.array([la_html])[0,0,:,:]
            ) \
            [[0,1,7]] \
            .dropna() \
            .rename(columns={0:'week', 1:'date', 7:'lanes'})
            
        la_data = pd.concat([la_data, la_df])
        la_data = la_data[~la_data.week.str.contains('Page')]

    # merge data and format columns
    la_data['date'] = la_data['date'].apply(lambda x: pd.to_datetime(x))

    df = pd.merge(left=data, right=la_data[['date', 'lanes']], on='date', how='left').drop_duplicates()

    df['lanes'] = df['lanes'].astype('int')
    
    def calc_pairing(lane):
        if (lane % 2) == 0:
            return f'{lane-1}/{lane}'
        else: return f'{lane}/{lane + 1}'
        
    df['lane_pair'] = df['lanes'].apply(lambda x: calc_pairing(x))

    df.to_pickle('scraped_bowler_data.pkl')
    pd.to_pickle(datetime.today(), 'lastsave.pkl')

    return None
