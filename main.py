import pandas as pd

#from get_data import get_players_stats
from clean_data import clean_stats, unique_players, consolidate_personal_awards

years = list(range(2001, 2023))
# stats that aren't need for model
columns_to_drop = ['Rk', 'Pos', 'FG', 'FGA', 'FG%', '3P',
                   '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%',
                   'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB',
                   'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
distinct_players = []
player_stats = {}

#get_players_stats(years)
personal_awards = consolidate_personal_awards()
for year in years:
    distinct_players.extend(unique_players(year))
    player_stats[year] = clean_stats(year, columns_to_drop)

distinct_players = set(distinct_players)

print(personal_awards)